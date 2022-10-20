/*
using fetch-api to like posts
by making GET-requests to Django LikeCreateView
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
  try {
    // First, I used GET method, but then decided to use POST because DB operations
    //fetch(this.href); // 'this' reffers to as addEventListener object abs url
    fetch("/api/v1/likes/add/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json;charset=utf-8",
        "X-CSRFToken": csrftoken,
      },
      body: JSON.stringify({"post": this.href.match(/(\d+)\/$/)[1]})
    });
  } catch(err) {
    // If error happend while fetching - the error will show in console,
    // but no like correction happend, because it automatically check in
    // next updatelike function that updates relevant number of likes and heart filling
    console.log(err);
  }
  // fetch(this.href); // 'this' reffers to as addEventListener object abs url
  // Get current heart+number
  let content = this.innerHTML.trim().split(" ");
  // Change hear to opposite color and increment or decrement number
  if (content[0].charCodeAt(0) === 10084) {
    content[0] = "&#9825;";
    --content[1];
  } else {
    content[0] = "&#10084;";
    ++content[1];
  }
  this.innerHTML = `${content[0]} ${content[1]}`;
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
    const response = await fetch(
      "/likes_count_on_post/" + like.href.match(/(\d+)\/$/)[1]
    ); // Here we have used relative url
    const data = await response.text();
    if (old_like !== data) {
      like.innerHTML = data;
    }
  });
};

// Updates likes (if exists) with interval of 3 sec
if (likes.length) setInterval(updateLike, 3000, likes);
