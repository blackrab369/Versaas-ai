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

// 30 fps sprite-strip player for 2.5D office
let canvas, ctx, stripImg, frame, frames, rafId;

function startOfficeAnimation() {
  // fetch strip URL
  fetch("/api/office/strip")
    .then((r) => r.json())
    .then((data) => {
      canvas = document.getElementById("office-canvas");
      ctx = canvas.getContext("2d");
      canvas.width = 256; // single frame size
      canvas.height = 256;
      stripImg = new Image();
      stripImg.src = data.url;
      stripImg.onload = () => {
        frames = data.frames;
        frame = 0;
        loop();
      };
    });
}

function loop() {
  ctx.clearRect(0, 0, 256, 256);
  ctx.drawImage(stripImg, frame * 256, 0, 256, 256, 0, 0, 256, 256);
  frame = (frame + 1) % frames;
  rafId = requestAnimationFrame(loop); // 60 fps native → we get ~30 fps
}

function stopOfficeAnimation() {
  if (rafId) cancelAnimationFrame(rafId);
}

// auto-start when DOM ready
document.addEventListener("DOMContentLoaded", startOfficeAnimation);
