/*
using fetch-api to like posts
by making GET-requests to Django LikeCreateView
*/

const likes = document.querySelectorAll(".like");

if (document.getElementById("user")) {
  likes.forEach(like => {
    like.addEventListener("click", async function(evt) {
      evt.preventDefault();
      await fetch(this.getAttribute("href"));
      let content = this.innerHTML.trim().split(" ");
      if (content[0].charCodeAt(0) === 10084) {
        content[0] = "&#9825;";
        --content[1];
      } else {
        content[0] = "&#10084;";
        ++content[1];
      }
      this.innerHTML = `${content[0]} ${content[1]}`;
    });
  });
}



// dynamically updates likes with interval of 3 sec.

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
    }
  );
};

setInterval(updateLike, 3000);
