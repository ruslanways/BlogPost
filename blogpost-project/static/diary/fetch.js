/*
using fetch-api to like posts
by making POST-requests to Django LikeCreateDestroyAPIView
*/

// Get cookie for any needs (e.g. csrftoken)
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}
const csrftoken = getCookie('csrftoken');

// Get all like <div>'s elements to operate with
const likes = document.querySelectorAll(".like");

// Send a get request to add or delete like
// Update a color and number of heart
function makeLike(evt) {
  // Prevent default browser following link behaviour
  // We could use not <a>, but then it would not be in the form of link-hand
  evt.preventDefault();

  // fetch(this.href); // 'this' reffers to as addEventListener object abs url
  // Get current heart+number
  let content = this.innerHTML.trim().split(" ");
  // Change hear to opposite color and increment or decrement number
  if (content[0].charCodeAt(0) === 10084) {
    content[0] = "&#9825;";
    // --content[1];
  } else {
    content[0] = "&#10084;";
    // ++content[1];
  }
  this.innerHTML = `${content[0]} ${content[1]}`;

  try {
    // 'this' reffers to as addEventListener object abs url
    fetch(this.href, {
      method: "POST",
      headers: {
        "Content-Type": "application/json;charset=utf-8",
        "X-CSRFToken": csrftoken,
      },
      body: JSON.stringify({"post": this.id})
    });
  } catch(err) {
    // If error happend while fetching - the error will show in console,
    // but no like correction happend, because it automatically check in
    // next updatelike function that updates relevant number of likes and heart filling
    console.log(err);
  }
}

// Add addEventListener to .like element
let readyForLike = like => like.addEventListener("click", makeLike);

// Add addEventListener on all .like elements
let onLikeClick = elm => elm.forEach(readyForLike);

// If the user is authenticated - start likes functionality
if (document.getElementById("user") && likes.length) onLikeClick(likes);



// Dynamically updates likes
let updateLike = elm => {
  elm.forEach(async function (like) {
    const old_like = like.innerHTML.trim();
    const response = await fetch("/likes_count_on_post/" + like.id + "/");
    const data = await response.text();
    if (old_like !== data) {
      like.innerHTML = data;
    }
  });
};

// Updates likes (if exists) with interval of 3 sec
// if (likes.length) setInterval(updateLike, 3000, likes);

let url = `ws://${window.location.host}/ws/socket-server/`;
const likeSocket = new WebSocket(url);

let posts_on_page = ["posts"];
for (let like of likes) {
  posts_on_page.push(+like.id);
}

// likeSocket.onopen = function(e) {
//   likeSocket.send(JSON.stringify({
//     'message': "Start connection"
//   }))
// }

console.log(posts_on_page);

likeSocket.onclose = function(e) {
  console.log("WebSocket closes unexpectedly");
};

likeSocket.onmessage = function(e) {
  let data = JSON.parse(e.data);
  console.log(data.message.split(",")[0]);
  console.log(posts_on_page.includes(+data.message.split(",")[0]));
  if (posts_on_page.includes(+data.message.split(",")[0])) {
    let like = document.getElementById(data["message"].split(",")[0]);
    const old_heart = like.innerHTML.split(" ")[0];
    const old_like = like.innerHTML.split(" ")[1];
    const new_like = data["message"].split(",")[1];
    if (old_like !== new_like) {
      like.innerHTML = old_heart+" "+new_like;
    }
  }
};
