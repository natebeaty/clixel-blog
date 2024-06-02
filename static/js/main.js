// Adjust aspect-ratio for "fitvid" videos
document.querySelectorAll('iframe[src*="youtube"], iframe[src*="vimeo"]').forEach((video) => {
  video.style.aspectRatio = `${video.getAttribute('width')} / ${video.getAttribute('height')}`
});
