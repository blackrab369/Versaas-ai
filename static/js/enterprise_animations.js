/**
 * Virsaas Virtual Software Inc. - Professional UI/UX Animations
 * Enhanced animations and smooth transitions for enterprise platform
 */

class EnterpriseAnimations {
  constructor() {
    this.init();
  }

  init() {
    this.setupScrollAnimations();
    this.setupHoverEffects();
    this.setupLoadingAnimations();
    this.setupModalAnimations();
    this.setupTransitionEffects();
  }

  // Smooth scroll animations for elements
  setupScrollAnimations() {
    const observerOptions = {
      threshold: 0.1,
      rootMargin: "0px 0px -50px 0px",
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("animate-in");
          entry.target.style.opacity = "1";
          entry.target.style.transform = "translateY(0)";
        }
      });
    }, observerOptions);

    // Observe elements for scroll animations
    document.querySelectorAll(".glass-effect, .hover-lift").forEach((el) => {
      el.style.opacity = "0";
      el.style.transform = "translateY(20px)";
      el.style.transition = "all 0.6s cubic-bezier(0.4, 0, 0.2, 1)";
      observer.observe(el);
    });
  }

  // Enhanced hover effects
  setupHoverEffects() {
    // Card hover effects
    document.querySelectorAll(".glass-effect").forEach((card) => {
      card.addEventListener("mouseenter", () => {
        card.style.transform = "translateY(-4px) scale(1.02)";
        card.style.boxShadow = "0 20px 40px rgba(0,0,0,0.3)";
      });

      card.addEventListener("mouseleave", () => {
        card.style.transform = "translateY(0) scale(1)";
        card.style.boxShadow = "0 10px 25px rgba(0,0,0,0.2)";
      });
    });

    // Button hover effects
    document.querySelectorAll("button").forEach((button) => {
      button.addEventListener("mouseenter", () => {
        button.style.transform = "translateY(-1px)";
        button.style.boxShadow = "0 4px 8px rgba(0,0,0,0.2)";
      });

      button.addEventListener("mouseleave", () => {
        button.style.transform = "translateY(0)";
        button.style.boxShadow = "none";
      });
    });
  }

  // Loading animations
  setupLoadingAnimations() {
    // Create loading spinner
    this.createLoadingSpinner();

    // Simulate loading states
    this.showLoadingState();
    setTimeout(() => this.hideLoadingState(), 2000);
  }

  createLoadingSpinner() {
    const spinner = document.createElement("div");
    spinner.id = "enterprise-loader";
    spinner.innerHTML = `
            <div class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center">
                <div class="glass-effect p-8 rounded-lg text-center">
                    <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-yellow-400 mx-auto mb-4"></div>
                    <div class="text-lg font-bold">Loading Virtual Office...</div>
                    <div class="text-sm opacity-75 mt-2">Initializing AI agents and simulation environment</div>
                </div>
            </div>
        `;
    document.body.appendChild(spinner);
  }

  showLoadingState() {
    const loader = document.getElementById("enterprise-loader");
    if (loader) {
      loader.style.display = "flex";
    }
  }

  hideLoadingState() {
    const loader = document.getElementById("enterprise-loader");
    if (loader) {
      loader.style.opacity = "0";
      setTimeout(() => {
        loader.style.display = "none";
        loader.style.opacity = "1";
      }, 300);
    }
  }

  // Modal animations
  setupModalAnimations() {
    // Enhanced modal show/hide with smooth transitions
    this.modalAnimations = {
      show: (modalId) => {
        const modal = document.getElementById(modalId);
        if (modal) {
          modal.classList.remove("hidden");
          modal.style.opacity = "0";
          modal.style.transform = "scale(0.9)";

          setTimeout(() => {
            modal.style.transition = "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)";
            modal.style.opacity = "1";
            modal.style.transform = "scale(1)";
          }, 10);
        }
      },

      hide: (modalId) => {
        const modal = document.getElementById(modalId);
        if (modal) {
          modal.style.transition = "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)";
          modal.style.opacity = "0";
          modal.style.transform = "scale(0.9)";

          setTimeout(() => {
            modal.classList.add("hidden");
            modal.style.opacity = "1";
            modal.style.transform = "scale(1)";
          }, 300);
        }
      },
    };
  }

  // Page transition effects
  setupTransitionEffects() {
    // Smooth page transitions
    document.querySelectorAll("a[href]").forEach((link) => {
      link.addEventListener("click", (e) => {
        const href = link.getAttribute("href");
        if (href && !href.startsWith("#") && !href.startsWith("javascript:")) {
          e.preventDefault();
          this.transitionToPage(href);
        }
      });
    });
  }

  transitionToPage(url) {
    // Fade out current content
    document.body.style.transition = "opacity 0.3s ease";
    document.body.style.opacity = "0";

    setTimeout(() => {
      window.location.href = url;
    }, 300);
  }

  // Particle system for background effects
  createParticleSystem() {
    const canvas = document.createElement("canvas");
    canvas.id = "particle-canvas";
    canvas.style.position = "fixed";
    canvas.style.top = "0";
    canvas.style.left = "0";
    canvas.style.width = "100%";
    canvas.style.height = "100%";
    canvas.style.pointerEvents = "none";
    canvas.style.zIndex = "1";
    canvas.style.opacity = "0.3";

    document.body.appendChild(canvas);

    const ctx = canvas.getContext("2d");
    const particles = [];

    // Resize canvas
    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };

    resizeCanvas();
    window.addEventListener("resize", resizeCanvas);

    // Particle class
    class Particle {
      constructor() {
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height;
        this.vx = (Math.random() - 0.5) * 0.5;
        this.vy = (Math.random() - 0.5) * 0.5;
        this.size = Math.random() * 2 + 1;
        this.opacity = Math.random() * 0.5 + 0.2;
      }

      update() {
        this.x += this.vx;
        this.y += this.vy;

        if (this.x < 0 || this.x > canvas.width) this.vx *= -1;
        if (this.y < 0 || this.y > canvas.height) this.vy *= -1;
      }

      draw() {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255, 255, 255, ${this.opacity})`;
        ctx.fill();
      }
    }

    // Create particles
    for (let i = 0; i < 50; i++) {
      particles.push(new Particle());
    }

    // Animation loop
    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      particles.forEach((particle) => {
        particle.update();
        particle.draw();
      });

      requestAnimationFrame(animate);
    };

    animate();
  }

  // Enhanced notification system
  showEnhancedNotification(message, type = "info", duration = 3000) {
    const notification = document.createElement("div");
    notification.className = `fixed top-4 right-4 p-4 rounded-lg z-50 max-w-sm transform translate-x-full transition-transform duration-300`;

    const colors = {
      success: "bg-green-600",
      error: "bg-red-600",
      info: "bg-blue-600",
      warning: "bg-yellow-600",
    };

    const icons = {
      success: "fas fa-check-circle",
      error: "fas fa-exclamation-circle",
      info: "fas fa-info-circle",
      warning: "fas fa-exclamation-triangle",
    };

    notification.className += ` ${colors[type]}`;
    notification.innerHTML = `
            <div class="flex items-center space-x-3">
                <i class="${icons[type]} text-xl"></i>
                <div class="flex-1">${message}</div>
                <button onclick="this.parentElement.parentElement.remove()" class="text-white hover:text-gray-200">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

    document.body.appendChild(notification);

    // Animate in
    setTimeout(() => {
      notification.style.transform = "translateX(0)";
    }, 100);

    // Auto remove
    setTimeout(() => {
      notification.style.transform = "translateX(full)";
      setTimeout(() => notification.remove(), 300);
    }, duration);
  }

  // Progress bar animations
  animateProgressBar(element, targetValue, duration = 1000) {
    const startValue = parseInt(element.style.width) || 0;
    const startTime = performance.now();

    const animate = (currentTime) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);

      // Easing function
      const easeOutCubic = 1 - Math.pow(1 - progress, 3);
      const currentValue =
        startValue + (targetValue - startValue) * easeOutCubic;

      element.style.width = currentValue + "%";

      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };

    requestAnimationFrame(animate);
  }

  // Number counting animation
  animateNumber(element, targetNumber, duration = 1000) {
    const startNumber = parseInt(element.textContent) || 0;
    const startTime = performance.now();

    const animate = (currentTime) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);

      // Easing function
      const easeOutCubic = 1 - Math.pow(1 - progress, 3);
      const currentNumber = Math.floor(
        startNumber + (targetNumber - startNumber) * easeOutCubic
      );

      element.textContent = currentNumber;

      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };

    requestAnimationFrame(animate);
  }

  // Enhanced tooltip system
  createEnhancedTooltip(content, position = "top") {
    const tooltip = document.createElement("div");
    tooltip.className =
      "enterprise-tooltip absolute z-50 glass-effect p-3 rounded-lg text-sm max-w-xs";
    tooltip.innerHTML = content;
    tooltip.style.opacity = "0";
    tooltip.style.transform = "translateY(10px)";
    tooltip.style.transition = "all 0.3s ease";

    document.body.appendChild(tooltip);

    // Position tooltip
    const rect = event.target.getBoundingClientRect();
    let left = rect.left + rect.width / 2 - tooltip.offsetWidth / 2;
    let top;

    switch (position) {
      case "top":
        top = rect.top - tooltip.offsetHeight - 10;
        break;
      case "bottom":
        top = rect.bottom + 10;
        break;
      case "left":
        left = rect.left - tooltip.offsetWidth - 10;
        top = rect.top + rect.height / 2 - tooltip.offsetHeight / 2;
        break;
      case "right":
        left = rect.right + 10;
        top = rect.top + rect.height / 2 - tooltip.offsetHeight / 2;
        break;
    }

    tooltip.style.left = left + "px";
    tooltip.style.top = top + "px";

    // Animate in
    setTimeout(() => {
      tooltip.style.opacity = "1";
      tooltip.style.transform = "translateY(0)";
    }, 10);

    return tooltip;
  }

  // Remove tooltip with animation
  removeTooltip(tooltip) {
    tooltip.style.opacity = "0";
    tooltip.style.transform = "translateY(10px)";
    setTimeout(() => tooltip.remove(), 300);
  }

  // Initialize typing animation for text elements
  initTypingAnimation() {
    document.querySelectorAll(".typing-animation").forEach((element) => {
      const text = element.textContent;
      element.textContent = "";
      element.style.borderRight = "2px solid #fff";

      let i = 0;
      const typeWriter = () => {
        if (i < text.length) {
          element.textContent += text.charAt(i);
          i++;
          setTimeout(typeWriter, 50);
        } else {
          element.style.borderRight = "none";
        }
      };

      typeWriter();
    });
  }

  // Enhanced chart animations
  animateChart(element, data, options = {}) {
    const defaultOptions = {
      duration: 1500,
      easing: "easeOutCubic",
    };

    const config = { ...defaultOptions, ...options };

    // Create animated chart using Plotly.js
    if (typeof Plotly !== "undefined") {
      Plotly.newPlot(element, data, {
        ...config,
        transition: {
          duration: config.duration,
          easing: config.easing,
        },
      });
    }
  }
}

// Initialize animations when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  const animations = new EnterpriseAnimations();

  // Add particle system for enhanced visual effects
  animations.createParticleSystem();

  // Initialize typing animations
  animations.initTypingAnimation();

  // Make animations globally available
  window.EnterpriseAnimations = animations;
});

// Export for module systems
if (typeof module !== "undefined" && module.exports) {
  module.exports = EnterpriseAnimations;
}
