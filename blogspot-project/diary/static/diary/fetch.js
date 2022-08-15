const likes = document.querySelectorAll(".like");

likes.forEach((like) => {
  like.addEventListener("click", async function (evt) {
    evt.preventDefault();
    await fetch(this.getAttribute("href"));
    let content = this.innerHTML.trim().split(" ");
    console.log(content);
    if (content[0].charCodeAt(0) === 10084) {
      content[0] = "&#9825;";
      content[1] = --content[1];
    } else {
      content[0] = "&#10084;";
      content[1] = ++content[1];
    }
    this.innerHTML = `${content[0]} ${content[1]}`;
  });
});
