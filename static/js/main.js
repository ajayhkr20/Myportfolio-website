document.addEventListener('DOMContentLoaded', () => {

    // Nav toggle
    const navToggle = document.getElementById('navToggle');
    const navLinks  = document.getElementById('navLinks');
    navToggle?.addEventListener('click', () => navLinks?.classList.toggle('open'));
    navLinks?.querySelectorAll('a').forEach(a => a.addEventListener('click', () => navLinks.classList.remove('open')));

    // Navbar scroll opacity
    const navbar = document.getElementById('navbar');
    window.addEventListener('scroll', () => {
        if (navbar) navbar.style.background = window.scrollY > 50
            ? 'rgba(15,17,23,0.98)' : 'rgba(15,17,23,0.88)';
    }, { passive: true });

    // Active nav link
    const sections = document.querySelectorAll('section[id], header[id]');
    const navItems = document.querySelectorAll('.nav-links a');
    new IntersectionObserver(entries => {
        entries.forEach(e => {
            if (e.isIntersecting) {
                navItems.forEach(a => a.classList.remove('active'));
                document.querySelector(`.nav-links a[href="#${e.target.id}"]`)?.classList.add('active');
            }
        });
    }, { threshold: 0.35 }).observe && sections.forEach(s =>
        new IntersectionObserver(entries => {
            entries.forEach(e => {
                if (e.isIntersecting) {
                    navItems.forEach(a => a.classList.remove('active'));
                    document.querySelector(`.nav-links a[href="#${e.target.id}"]`)?.classList.add('active');
                }
            });
        }, { threshold: 0.35 }).observe(s)
    );

    // Scroll reveal
    const reveals = document.querySelectorAll('.reveal');
    new IntersectionObserver(entries => {
        entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('visible'); } });
    }, { threshold: 0.1 }).observe && reveals.forEach(el =>
        new IntersectionObserver(entries => {
            entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
        }, { threshold: 0.1 }).observe(el)
    );

    // Hero card tilt
    const hcard = document.querySelector('.hero-card');
    hcard?.addEventListener('mousemove', e => {
        const r = hcard.getBoundingClientRect();
        const x = (e.clientX - r.left) / r.width  - .5;
        const y = (e.clientY - r.top)  / r.height - .5;
        hcard.style.transform = `perspective(800px) rotateY(${x*7}deg) rotateX(${-y*7}deg) translateY(-4px)`;
    });
    hcard?.addEventListener('mouseleave', () => hcard.style.transform = '');

    // Typed hero title
    const titleEl = document.querySelector('.hero-title');
    if (titleEl) {
        const titles = [titleEl.textContent.trim(), 'Backend Developer', 'Django Specialist', 'REST API Engineer'];
        let ti = 0, ci = 0, del = false;
        function type() {
            const cur = titles[ti];
            titleEl.textContent = del ? cur.slice(0, --ci) : cur.slice(0, ++ci);
            if (!del && ci === cur.length) { del = true; setTimeout(type, 1800); return; }
            if (del && ci === 0) { del = false; ti = (ti + 1) % titles.length; }
            setTimeout(type, del ? 45 : 75);
        }
        setTimeout(type, 1200);
    }

    // Toast auto-dismiss
    document.querySelectorAll('.toast').forEach(t => {
        setTimeout(() => { t.style.opacity = '0'; t.style.transform = 'translateX(100%)'; setTimeout(() => t.remove(), 300); }, 4000);
    });
});
