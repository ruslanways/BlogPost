/*
using fetch-api to like posts
by making GET-requests to Django LikeCreateView
*/

// Get all like <div>'s elements to operate with
const likes = document.querySelectorAll(".like");

// Send a get request to add or delete like
// Update a color and number of heart
async function makeLike(event) {
  event.preventDefault();
  await fetch(this.href); // 'this' reffers to as addEventListener object
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
let readyForLike = function (like) {
  like.addEventListener("click", makeLike);
};

// Add addEventListener on all .like elements
let onLikeClick = function () {
  likes.forEach(readyForLike);
};

// If the user is authenticated - start likes functionality
if (document.getElementById("user")) {
  onLikeClick();
}



// Dynamically updates likes
let updateLike = () => {
  likes.forEach(async function (like) {
    const old_like = like.innerHTML.trim();
    const response = await fetch(
      "/likes_count_on_post/" + like.getAttribute("href").split("/")[3]
    );
    const data = await response.text();
    if (old_like !== data) {
      like.innerHTML = data;
    }
  });
};

// Updates likes with interval of 3 sec
setInterval(updateLike, 3000);
