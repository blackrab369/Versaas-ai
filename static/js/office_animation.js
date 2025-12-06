document.addEventListener("DOMContentLoaded", function () {
  const officeContainer = document.getElementById("office-container");
  const images = [
    "/path/to/office/frame1.png",
    "/path/to/office/frame2.png",
    // Add more frames as needed
  ];
  let currentFrame = 0;

  function updateFrame() {
    officeContainer.src = images[currentFrame];
    currentFrame = (currentFrame + 1) % images.length;
  }

  setInterval(updateFrame, 100); // Change frame every 100ms
});
