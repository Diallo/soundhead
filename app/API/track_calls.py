from flask_restplus import Namespace, Resource, fields
from app.utils.tasks import find_song_recommendations
from app.utils import influx, models
from app import app

import dateparser
import datetime

api = Namespace('tracks', description='Information about tracks (over time)', path="/tracks")

history = api.model('Song history with mood', {
    'userid': fields.String,
    'mean_excitedness': fields.Float,
    'mean_happiness': fields.Float,
    'songs': fields.Nested(api.model('song', {
        'songid': fields.String,
        'name': fields.String,
        'time': fields.String,
        'excitedness': fields.Float,
        'happiness': fields.Float
    }))
})


@api.route('/history/<string:userid>/<int:song_count>')
@api.response(404, 'No history found')
class History(Resource):
    @api.marshal_with(history, envelope='resource')
    def get(self, userid, song_count):
        """
        Obtain N most recently played songs along with their mood.
        """
        querycount = 3 * song_count
        client = influx.create_client(app.config['INFLUX_HOST'], app.config['INFLUX_PORT'])
        recent_songs = client.query(f'select songid from "{userid}" order by time desc limit {querycount}')
        if recent_songs:
            history = []
            recent_song_list = list(recent_songs.get_points(measurement=userid))
            songids = list(set([song['songid'] for song in recent_song_list]))
            songids = songids[:song_count] if song_count > 0 else songids
            songmoods = models.Songmood.get_moods(songids)
            excitedness = 0
            happiness = 0
            mean_count = 1

            for songmood in songmoods:
                if songmood.excitedness and songmood.happiness:
                    excitedness += songmood.excitedness
                    happiness += songmood.happiness
                    mean_count += 1 if mean_count != 1 else 0
                song = {}
                song['songid'] = songmood.songid
                song['excitedness'] = songmood.excitedness
                song['happiness'] = songmood.happiness
                song['time'] = [song['time'] for song in recent_song_list][0]
                song['name'] = models.Song.get_song_name(song['songid'])
                history.append(song)
            excitedness /= mean_count
            happiness /= mean_count

            return {
                'userid': userid,
                'mean_excitedness': excitedness,
                'mean_happiness': happiness,
                'songs': history
            }
        else:
            api.abort(404, message=f"No history not found for '{userid}'")


possible_metrics = ['acousticness', 'danceability', 'duration_ms', 'energy',
                    'instrumentalness', 'key', 'liveness', 'loudness', 'mode',
                    'speechiness', 'tempo', 'valence']


def parse_time(start, end):
    if start in ('beginning of time' or 'the beginning of time'):
        start = "0"

    start_date = dateparser.parse(start)
    if not start_date:
        api.abort(400, message=f"could not parse '{start}' as start date")

    end_date = dateparser.parse(end)
    if not end_date:
        api.abort(400, message=f"could not parse '{end}' as end date")

    return f"'{start_date.isoformat()}Z'", f"'{end_date.isoformat()}Z'"


metrics = api.model('Metric over time', {
    'userid': fields.String,
    'metric_over_time': fields.Nested(api.model('metric', {
        'time': fields.String,
        'value': fields.Float,
    }))
})


@api.route('/metrics/<string:userid>/<string:metrics>/<string:song_count>')
@api.response(400, 'Invalid metric')
@api.response(404, 'No metrics found')
class Metric(Resource):
    @api.marshal_with(metrics, envelope='resource')
    def get(self, userid, metrics, song_count=50, start="'1678-09-21T00:20:43.145224194Z'",
            end=str("'" + datetime.datetime.now().isoformat() + "Z'")):
        """
        Obtain metrics of a user within a given timeframe.
        Possible metrics:
        'acousticness', 'danceability', 'duration_ms', 'energy',
        'instrumentalness', 'key', 'liveness', 'loudness', 'mode',
        'speechiness', 'tempo', 'valence'
        """
        for metric in metrics.split(','):
            if metric.strip() not in possible_metrics:
                api.abort(400, message=f"invalid metric")

        print('\n\n\n\n\n')
        metrics = ','.join(['\"' + metric.strip() + '\"' for metric in metrics.split(',')])

        client = influx.create_client(app.config['INFLUX_HOST'], app.config['INFLUX_PORT'])
        user_metrics = client.query(f'select {metrics} from "{userid}" limit {song_count}')
        if user_metrics:
            metric_list = list(user_metrics.get_points(measurement=userid))
            print(metric_list)
            print('-----------------------------------------')

            for timed_metric in metric_list:
                timed_metric['value'] = timed_metric.pop('tempo')

            return {
                'userid': userid,
                'metric_over_time': metric_list
            }
        else:
            api.abort(404, message=f"No metrics found for '{userid}'")


top_genres = api.model('Top x genres', {
    'userid': fields.String,
    'genres': fields.Nested(api.model('topgenres', {
        'genre': fields.String,
        'count': fields.Integer
    }))
})


@api.route('/genres/<string:userid>/<string:count>')
class TopGenres(Resource):
    @api.marshal_with(top_genres, envelope='resource')
    def get(self, userid, count):
        """Get the top N genres of the user."""
        client = influx.create_client(app.config['INFLUX_HOST'], app.config['INFLUX_PORT'])
        recent_songs = client.query(f'select songid from "{userid}" order by time desc')
        if not recent_songs:
            print('no history found')
            return
        recent_song_list = list(recent_songs.get_points(measurement=userid))
        songids = list(set([song['songid'] for song in recent_song_list]))
        # TODO you can't do this here
        # Artist.query(genres).filter()


recommendations = api.model('Song recommendations', {
    'userid': fields.String,
    'recommendations': fields.Nested(api.model('recommendation', {
        'songid': fields.String,
        'excitedness': fields.String,
        'happiness': fields.List(fields.String)
    }))
})


@api.route('/recommendation/<string:userid>/<int:recommendation_count>')
@api.response(404, 'No recommendations found')
class Recommendation_user(Resource):
    @api.marshal_with(recommendations, envelope='resource')
    def get(self, userid, recommendation_count):
        """
        Obtain recommendations for the user along with their features.
        """
        client = influx.create_client(app.config['INFLUX_HOST'], app.config['INFLUX_PORT'])
        recent_songs = client.query(f'select songid from "{userid}" order by time desc limit 5')
        if recent_songs:
            recent_songs = list(recent_songs.get_points(measurement=userid))
            songids = [song['songid'] for song in recent_songs]
            recs = find_song_recommendations(songids, userid, recommendation_count)
            if recs:
                return {
                    'userid': userid,
                    'recommendations': recs
                }
            else:
                api.abort(404, message=f"No recommendations not found for '{userid}'")


@api.route('/recommendation/<string:userid>/<string:songid>/<float:excitedness>/<float:happiness>')
@api.response(404, 'No recommendations found')
class Recommendation_song(Resource):
    @api.marshal_with(recommendations, envelope='resource')
    def get(self, userid, songid, excitedness, happiness):
        """
        Obtain recommendations based on a song along with its excitedness and happiness.
        """
        recs = find_song_recommendations([songid], userid, 10)
        if recs:
            return {
                'userid': userid,
                'recommendations': recs
            }
        else:
            api.abort(404, message=f"No recommendations not found for '{userid}'")
