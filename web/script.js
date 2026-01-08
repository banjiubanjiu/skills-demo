// ==========================================
// CLAUDE SKILLS SHOWCASE - INTERACTIVE SCRIPTS
// ==========================================

document.addEventListener('DOMContentLoaded', () => {
    // Initialize all interactive features
    initCardTiltEffect();
    initSmoothScroll();
    initScrollAnimations();
    initParallaxEffect();
});

// --- 3D Tilt Effect for Cards ---
function initCardTiltEffect() {
    const cards = document.querySelectorAll('.skill-card, .intro-card, .benefit-card');

    cards.forEach(card => {
        card.addEventListener('mousemove', handleCardMouseMove);
        card.addEventListener('mouseleave', handleCardMouseLeave);
    });
}

function handleCardMouseMove(e) {
    const card = e.currentTarget;
    const rect = card.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const centerX = rect.width / 2;
    const centerY = rect.height / 2;

    const rotateX = (y - centerY) / 20;
    const rotateY = (centerX - x) / 20;

    card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-4px)`;
}

function handleCardMouseLeave(e) {
    const card = e.currentTarget;
    card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateY(0)';
}

// --- Smooth Scroll for Navigation ---
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// --- Scroll Animations ---
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe all cards and sections
    const elementsToAnimate = document.querySelectorAll(
        '.skill-card, .intro-card, .benefit-card, .step-item, .section-title'
    );

    elementsToAnimate.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
}

// Add animate-in styles dynamically
const style = document.createElement('style');
style.textContent = `
    .animate-in {
        opacity: 1 !important;
        transform: translateY(0) !important;
    }
`;
document.head.appendChild(style);

// --- Parallax Effect for Decorations ---
function initParallaxEffect() {
    const decorations = document.querySelectorAll('.deco-line, .deco-circle');

    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;

        decorations.forEach((deco, index) => {
            const speed = 0.1 + (index * 0.05);
            const yPos = -(scrolled * speed);
            deco.style.transform = `translateY(${yPos}px)`;
        });
    });
}

// --- Trigger Tag Click Effect ---
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('trigger-tag')) {
        // Create ripple effect
        const ripple = document.createElement('span');
        ripple.style.position = 'absolute';
        ripple.style.width = '100%';
        ripple.style.height = '100%';
        ripple.style.background = 'rgba(6, 182, 212, 0.3)';
        ripple.style.borderRadius = 'inherit';
        ripple.style.animation = 'ripple 0.6s ease-out';

        e.target.style.position = 'relative';
        e.target.style.overflow = 'hidden';
        e.target.appendChild(ripple);

        setTimeout(() => ripple.remove(), 600);
    }
});

// Add ripple animation
const rippleStyle = document.createElement('style');
rippleStyle.textContent = `
    @keyframes ripple {
        from {
            transform: scale(0);
            opacity: 1;
        }
        to {
            transform: scale(2);
            opacity: 0;
        }
    }
`;
document.head.appendChild(rippleStyle);

// --- Typing Effect Reset on Scroll ---
let typingEffectReset = false;
const terminalPrompt = document.querySelector('.terminal-prompt');

if (terminalPrompt) {
    const resetTypingObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !typingEffectReset) {
                // Reset typing animation when scrolled back into view
                const typingText = document.querySelector('.typing-text');
                if (typingText) {
                    typingText.style.animation = 'none';
                    setTimeout(() => {
                        typingText.style.animation = 'typing 3s steps(35) forwards, blink 0.7s step-end infinite';
                    }, 100);
                }
                typingEffectReset = true;
            }
        });
    }, { threshold: 0.5 });

    resetTypingObserver.observe(terminalPrompt);
}

// --- Console Easter Egg ---
console.log('%c🚀 Claude Skills Showcase', 'font-size: 24px; font-weight: bold; color: #06b6d4;');
console.log('%cBuilt with Neo-Brutalist Terminal Aesthetic', 'font-size: 14px; color: #84cc16;');
console.log('%cExplore the power of Claude Code Skills!', 'font-size: 12px; color: #94a3b8;');