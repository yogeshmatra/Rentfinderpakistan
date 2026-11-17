/**
 * Rent Finder Pakistan - Main Core JavaScript
 * 3D WebGL Canvas Animation, 3D Card Tilt, Navigation, Favorites & Compare System
 */

document.addEventListener('DOMContentLoaded', () => {
  initHeaderScroll();
  init3DHeroCanvas();
  init3DCardTilt();
  initFavorites();
  initCompareSystem();
  initMobileNav();
});

/* ==========================================================================
   1. HEADER SCROLL TRANSITION
   ========================================================================== */
function initHeaderScroll() {
  const header = document.querySelector('.site-header');
  if (!header) return;

  window.addEventListener('scroll', () => {
    if (window.scrollY > 40) {
      header.classList.add('scrolled');
    } else {
      header.classList.remove('scrolled');
    }
  }, { passive: true });
}

/* ==========================================================================
   2. 3D WEBGL HERO CANVAS (Particle Mesh & Architectural Lines)
   Inspired by USTA Agency WebGL Hero Visuals from Pinterest Research
   ========================================================================== */
function init3DHeroCanvas() {
  const canvas = document.getElementById('webgl-hero-canvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  let width = canvas.width = window.innerWidth;
  let height = canvas.height = canvas.parentElement.offsetHeight || window.innerHeight;

  window.addEventListener('resize', () => {
    width = canvas.width = window.innerWidth;
    height = canvas.height = canvas.parentElement.offsetHeight || window.innerHeight;
  });

  // Mouse Parallax coordinates
  let mouse = { x: width / 2, y: height / 2, targetX: width / 2, targetY: height / 2 };
  window.addEventListener('mousemove', (e) => {
    mouse.targetX = e.clientX;
    mouse.targetY = e.clientY;
  });

  // Generate glowing 3D depth particles
  const particleCount = Math.min(100, Math.floor(width / 15));
  const particles = [];

  for (let i = 0; i < particleCount; i++) {
    particles.push({
      x: Math.random() * width,
      y: Math.random() * height,
      z: Math.random() * 800 + 100,
      radius: Math.random() * 2 + 1,
      baseRadius: Math.random() * 2 + 1,
      color: Math.random() > 0.45 ? '16, 185, 129' : '0, 200, 255', // Emerald & Cyan
      speedX: (Math.random() - 0.5) * 0.4,
      speedY: (Math.random() - 0.5) * 0.4
    });
  }

  // Animation Loop
  function render() {
    ctx.clearRect(0, 0, width, height);

    // Smooth mouse dampening
    mouse.x += (mouse.targetX - mouse.x) * 0.05;
    mouse.y += (mouse.targetY - mouse.y) * 0.05;

    const offsetX = (mouse.x - width / 2) * 0.04;
    const offsetY = (mouse.y - height / 2) * 0.04;

    // Draw connected architectural constellation lines
    for (let i = 0; i < particles.length; i++) {
      const p = particles[i];
      p.x += p.speedX;
      p.y += p.speedY;

      if (p.x < 0) p.x = width;
      if (p.x > width) p.x = 0;
      if (p.y < 0) p.y = height;
      if (p.y > height) p.y = 0;

      const px = p.x + offsetX * (800 / p.z);
      const py = p.y + offsetY * (800 / p.z);
      const alpha = Math.max(0.1, (1000 - p.z) / 1000 * 0.7);

      // Connect near particles
      for (let j = i + 1; j < particles.length; j++) {
        const p2 = particles[j];
        const p2x = p2.x + offsetX * (800 / p2.z);
        const p2y = p2.y + offsetY * (800 / p2.z);
        const dist = Math.hypot(px - p2x, py - p2y);

        if (dist < 120) {
          ctx.beginPath();
          ctx.strokeStyle = `rgba(${p.color}, ${(1 - dist / 120) * 0.18})`;
          ctx.lineWidth = 0.8;
          ctx.moveTo(px, py);
          ctx.lineTo(p2x, p2y);
          ctx.stroke();
        }
      }

      // Draw particle dot
      ctx.beginPath();
      ctx.fillStyle = `rgba(${p.color}, ${alpha})`;
      ctx.arc(px, py, p.radius, 0, Math.PI * 2);
      ctx.fill();
    }

    requestAnimationFrame(render);
  }

  render();
}

/* ==========================================================================
   3. 3D CARD TILT EFFECT (Interactive Perspective Rotation)
   ========================================================================== */
function init3DCardTilt() {
  const cards = document.querySelectorAll('.property-card, .tilt-element');

  cards.forEach(card => {
    card.addEventListener('mousemove', e => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      const centerX = rect.width / 2;
      const centerY = rect.height / 2;

      const rotateX = ((y - centerY) / centerY) * -7;
      const rotateY = ((x - centerX) / centerX) * 7;

      card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`;
    });

    card.addEventListener('mouseleave', () => {
      card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)';
    });
  });
}

/* ==========================================================================
   4. FAVORITES SYSTEM (AJAX Sync with Database)
   ========================================================================== */
function initFavorites() {
  document.querySelectorAll('.btn-fav').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      e.preventDefault();
      e.stopPropagation();

      const propId = btn.dataset.propId;
      if (!propId) return;

      try {
        const response = await fetch('/api/favorites/toggle', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ property_id: propId })
        });

        if (response.status === 401) {
          showToast('Please login to save properties to your favorites.', 'warning');
          setTimeout(() => { window.location.href = '/login?next=' + encodeURIComponent(window.location.pathname); }, 1500);
          return;
        }

        const data = await response.json();
        if (data.success) {
          btn.classList.toggle('active', data.is_saved);
          const icon = btn.querySelector('i');
          if (icon) {
            icon.className = data.is_saved ? 'fas fa-heart' : 'far fa-heart';
          }

          // Update header badge if exists
          const badge = document.querySelector('.favorites-badge-count');
          if (badge) badge.textContent = data.total_saved;

          showToast(data.message, data.is_saved ? 'success' : 'info');
        }
      } catch (err) {
        console.error('Error toggling favorite:', err);
      }
    });
  });
}

/* ==========================================================================
   5. PROPERTY COMPARE SYSTEM
   ========================================================================== */
function initCompareSystem() {
  const getCompareList = () => {
    try {
      return JSON.parse(localStorage.getItem('rentfinder_compare_ids') || '[]');
    } catch {
      return [];
    }
  };

  const updateCompareUI = () => {
    const list = getCompareList();
    const countBadge = document.querySelector('.compare-badge-count');
    if (countBadge) countBadge.textContent = list.length;
  };

  window.toggleCompare = function(propId) {
    let list = getCompareList();
    const id = parseInt(propId);

    if (list.includes(id)) {
      list = list.filter(item => item !== id);
      showToast('Property removed from comparison tray.', 'info');
    } else {
      if (list.length >= 4) {
        showToast('You can compare a maximum of 4 properties at once.', 'warning');
        return;
      }
      list.push(id);
      showToast('Property added to comparison list!', 'success');
    }

    localStorage.setItem('rentfinder_compare_ids', JSON.stringify(list));
    updateCompareUI();
  };

  window.openComparePage = function() {
    const list = getCompareList();
    if (list.length === 0) {
      showToast('No properties selected for comparison. Add properties first!', 'warning');
      return;
    }
    window.location.href = `/compare?ids=${list.join(',')}`;
  };

  updateCompareUI();
}

/* ==========================================================================
   6. MOBILE NAVIGATION DRAWER
   ========================================================================== */
function initMobileNav() {
  const toggleBtn = document.querySelector('.mobile-nav-toggle');
  const drawer = document.querySelector('.mobile-drawer');

  if (toggleBtn && drawer) {
    toggleBtn.addEventListener('click', () => {
      drawer.classList.toggle('open');
      document.body.classList.toggle('no-scroll');
    });

    const closeBtn = drawer.querySelector('.close-drawer');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => {
        drawer.classList.remove('open');
        document.body.classList.remove('no-scroll');
      });
    }
  }
}

/* ==========================================================================
   7. TOAST NOTIFICATIONS HELPER
   ========================================================================== */
function showToast(message, type = 'info') {
  let container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;

  const iconMap = {
    success: 'fas fa-check-circle',
    danger: 'fas fa-exclamation-circle',
    warning: 'fas fa-exclamation-triangle',
    info: 'fas fa-info-circle'
  };

  toast.innerHTML = `
    <i class="${iconMap[type] || iconMap.info}"></i>
    <span>${message}</span>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}
