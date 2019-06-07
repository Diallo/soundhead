var songs = {{ songs }}
var song_count = {{ song_count }}
var genres = {{ genres }}
var genre_count = {{ genre_count }}
var timestamps = {{ timestamps }}
var duration = {{ duration }}

function randomColor() {
  return '#'+(0x1000000+(Math.random())*0xffffff).toString(16).substr(1,6)
}

var songs_colors = [for (i of songs) randomColor()];
var genres_colors = [for (i of genres) randomColor()]

new Chart(document.getElementById("barchart"), {
  type: 'bar',
  data: {
    labels: songs,
    datasets: [
      {
        label: "Count",
        backgroundColor: songs_colors,
        data: song_count
      }
    ]
  },
  options: {
    legend: { display: false },
    title: {
      display: true,
      text: 'Top 10 most listened to songs'
    }
  }
});

new Chart(document.getElementById("piechart"), {
  type: 'pie',
  data: {
    labels: genres,
    datasets: [{
      label: "count",
      backgroundColor: genres_colors,
      data: genre_count
    }]
  },
  options: {
    title: {
      display: true,
      text: 'Your top 10 genres'
    }
  }
});

new Chart(document.getElementById("linechart"), {
  type: 'line',
  data: {
    labels: timestamps,
    datasets: [{ 
        data: duration,
        label: "listen time (min)",
        }]
  },
  options: {
    title: {
      display: true,
      text: 'Total listening time over time'
    }
  }
});
