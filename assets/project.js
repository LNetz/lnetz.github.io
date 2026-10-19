// Project pages: YouTube videos load only on click (no request to YouTube before that).
// Without JS the facade is a plain link to the video.
document.querySelectorAll("a.yt[data-yt]").forEach(a => {
  a.addEventListener("click", e => {
    e.preventDefault();
    const f = document.createElement("iframe");
    f.src = `https://www.youtube-nocookie.com/embed/${a.dataset.yt}?autoplay=1&rel=0`;
    f.title = a.getAttribute("aria-label") || "YouTube";
    f.allow = "autoplay; encrypted-media; picture-in-picture; fullscreen";
    f.allowFullscreen = true;
    a.replaceWith(f);
    f.focus();
  });
});
