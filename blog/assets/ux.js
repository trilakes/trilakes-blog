/**
 * Tri-Lakes Blog UX Enhancements
 * Adds reading progress, back-to-top, smooth scrolling, and more
 */

(function() {
    'use strict';

    // Wait for DOM
    document.addEventListener('DOMContentLoaded', init);

    function init() {
        createReadingProgress();
        createBackToTop();
        enhanceTOCLinks();
        addCopyLinkToHeadings();
        lazyLoadImages();
    }

    // ================================
    // READING PROGRESS BAR
    // ================================
    function createReadingProgress() {
        // Only on article pages
        if (!document.querySelector('.post-content')) return;

        const progress = document.createElement('div');
        progress.className = 'reading-progress';
        progress.setAttribute('role', 'progressbar');
        progress.setAttribute('aria-label', 'Reading progress');
        document.body.prepend(progress);

        function updateProgress() {
            const article = document.querySelector('.post-content');
            if (!article) return;

            const articleTop = article.offsetTop;
            const articleHeight = article.offsetHeight;
            const windowHeight = window.innerHeight;
            const scrollY = window.scrollY;

            // Calculate progress
            const start = articleTop - windowHeight / 2;
            const end = articleTop + articleHeight - windowHeight / 2;
            const current = scrollY - start;
            const total = end - start;
            
            let percent = Math.min(Math.max((current / total) * 100, 0), 100);
            progress.style.width = percent + '%';
        }

        window.addEventListener('scroll', throttle(updateProgress, 10), { passive: true });
        updateProgress();
    }

    // ================================
    // BACK TO TOP BUTTON
    // ================================
    function createBackToTop() {
        const btn = document.createElement('button');
        btn.className = 'back-to-top';
        btn.innerHTML = '↑';
        btn.setAttribute('aria-label', 'Back to top');
        btn.setAttribute('title', 'Back to top');
        document.body.appendChild(btn);

        function toggleVisibility() {
            if (window.scrollY > 400) {
                btn.classList.add('visible');
            } else {
                btn.classList.remove('visible');
            }
        }

        btn.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });

        window.addEventListener('scroll', throttle(toggleVisibility, 100), { passive: true });
        toggleVisibility();
    }

    // ================================
    // ENHANCE TOC LINKS
    // ================================
    function enhanceTOCLinks() {
        const tocLinks = document.querySelectorAll('.toc a');
        const headings = [];

        tocLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href && href.startsWith('#')) {
                const target = document.getElementById(href.slice(1));
                if (target) {
                    headings.push({ link, target });
                }
            }
        });

        if (headings.length === 0) return;

        function highlightCurrent() {
            const scrollY = window.scrollY + 150;
            let current = headings[0];

            headings.forEach(item => {
                if (item.target.offsetTop <= scrollY) {
                    current = item;
                }
            });

            headings.forEach(item => {
                item.link.classList.remove('active');
            });
            current.link.classList.add('active');
        }

        window.addEventListener('scroll', throttle(highlightCurrent, 100), { passive: true });
        highlightCurrent();

        // Add active style
        const style = document.createElement('style');
        style.textContent = `
            .toc a.active {
                color: var(--secondary-color);
                font-weight: 600;
                padding-left: 15px;
                border-left: 2px solid var(--secondary-color);
            }
        `;
        document.head.appendChild(style);
    }

    // ================================
    // COPY LINK ON HEADING CLICK
    // ================================
    function addCopyLinkToHeadings() {
        const headings = document.querySelectorAll('.post-content h2[id], .post-content h3[id]');
        
        headings.forEach(heading => {
            heading.style.cursor = 'pointer';
            heading.title = 'Click to copy link to this section';
            
            heading.addEventListener('click', function() {
                const url = window.location.origin + window.location.pathname + '#' + heading.id;
                
                if (navigator.clipboard) {
                    navigator.clipboard.writeText(url).then(() => {
                        showToast('Link copied to clipboard!');
                    }).catch(() => {
                        fallbackCopy(url);
                    });
                } else {
                    fallbackCopy(url);
                }
            });
        });
    }

    function fallbackCopy(text) {
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        try {
            document.execCommand('copy');
            showToast('Link copied to clipboard!');
        } catch (e) {
            showToast('Failed to copy link');
        }
        document.body.removeChild(textarea);
    }

    function showToast(message) {
        // Remove existing toast
        const existing = document.querySelector('.toast-notification');
        if (existing) existing.remove();

        const toast = document.createElement('div');
        toast.className = 'toast-notification';
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed;
            bottom: 100px;
            left: 50%;
            transform: translateX(-50%);
            background: var(--primary-color, #0f0f0f);
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            font-size: 0.9rem;
            z-index: 10000;
            animation: toastIn 0.3s ease-out;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        `;
        document.body.appendChild(toast);

        // Add animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes toastIn {
                from { opacity: 0; transform: translateX(-50%) translateY(20px); }
                to { opacity: 1; transform: translateX(-50%) translateY(0); }
            }
            @keyframes toastOut {
                from { opacity: 1; transform: translateX(-50%) translateY(0); }
                to { opacity: 0; transform: translateX(-50%) translateY(20px); }
            }
        `;
        document.head.appendChild(style);

        setTimeout(() => {
            toast.style.animation = 'toastOut 0.3s ease-out forwards';
            setTimeout(() => toast.remove(), 300);
        }, 2500);
    }

    // ================================
    // LAZY LOAD IMAGES
    // ================================
    function lazyLoadImages() {
        if ('loading' in HTMLImageElement.prototype) {
            // Native lazy loading
            document.querySelectorAll('img:not([loading])').forEach(img => {
                img.setAttribute('loading', 'lazy');
            });
        } else {
            // Fallback with IntersectionObserver
            const images = document.querySelectorAll('img[data-src]');
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        observer.unobserve(img);
                    }
                });
            }, { rootMargin: '100px' });

            images.forEach(img => observer.observe(img));
        }
    }

    // ================================
    // UTILITY: THROTTLE
    // ================================
    function throttle(fn, wait) {
        let lastTime = 0;
        return function(...args) {
            const now = Date.now();
            if (now - lastTime >= wait) {
                lastTime = now;
                fn.apply(this, args);
            }
        };
    }

})();
