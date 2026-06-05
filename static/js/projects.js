(function () {
  'use strict';

  const TECH = {
    python:     { icon: 'fab fa-python',      color: '#3776ab', label: 'Python'     },
    django:     { icon: 'fas fa-layer-group', color: '#0d6e3e', label: 'Django'     },
    javascript: { icon: 'fab fa-js-square',   color: '#f7df1e', label: 'JavaScript' },
    js:         { icon: 'fab fa-js-square',   color: '#f7df1e', label: 'JS'         },
    react:      { icon: 'fab fa-react',       color: '#61dafb', label: 'React'      },
    html:       { icon: 'fab fa-html5',       color: '#e44d26', label: 'HTML5'      },
    css:        { icon: 'fab fa-css3-alt',    color: '#264de4', label: 'CSS3'       },
    docker:     { icon: 'fab fa-docker',      color: '#0db7ed', label: 'Docker'     },
    aws:        { icon: 'fab fa-aws',         color: '#ff9900', label: 'AWS'        },
    git:        { icon: 'fab fa-git-alt',     color: '#f05032', label: 'Git'        },
    github:     { icon: 'fab fa-github',      color: '#e2e8f0', label: 'GitHub'     },
    linux:      { icon: 'fab fa-linux',       color: '#fcc624', label: 'Linux'      },
    postgresql: { icon: 'fas fa-database',    color: '#336791', label: 'PostgreSQL' },
    postgres:   { icon: 'fas fa-database',    color: '#336791', label: 'Postgres'   },
    sql:        { icon: 'fas fa-database',    color: '#336791', label: 'SQL'        },
    redis:      { icon: 'fas fa-memory',      color: '#dc2626', label: 'Redis'      },
    nginx:      { icon: 'fas fa-server',      color: '#22c55e', label: 'Nginx'      },
    rest:       { icon: 'fas fa-plug',        color: '#3b82f6', label: 'REST API'   },
    api:        { icon: 'fas fa-plug',        color: '#3b82f6', label: 'API'        },
    celery:     { icon: 'fas fa-tasks',       color: '#a3e635', label: 'Celery'     },
    sqlite:     { icon: 'fas fa-database',    color: '#94a3b8', label: 'SQLite'     },
    flask:      { icon: 'fas fa-flask',       color: '#e2e8f0', label: 'Flask'      },
    node:       { icon: 'fab fa-node-js',     color: '#3c873a', label: 'Node.js'    },
  };

  function techInfo(raw) {
    const k = raw.toLowerCase().replace(/[^a-z]/g, '');
    return TECH[k] || { icon: 'fas fa-code', color: '#94a3b8', label: raw };
  }

  /* 1. Starfield */
  function initStarfield() {
    const canvas = document.getElementById('projects-canvas');
    const section = document.getElementById('projects');
    if (!canvas || !section) return;
    const ctx = canvas.getContext('2d');
    let W, H, stars = [];
    function resize() { W = canvas.width = section.offsetWidth; H = canvas.height = section.offsetHeight; }
    function mkS() { return { x:Math.random()*W, y:Math.random()*H, r:Math.random()*1.2+.2, vx:(Math.random()-.5)*.1, vy:-(Math.random()*.2+.04), a:Math.random(), da:(Math.random()*.005+.002)*(Math.random()<.5?1:-1) }; }
    resize(); stars = Array.from({length:120}, mkS);
    function draw() {
      ctx.clearRect(0,0,W,H);
      stars.forEach(s => {
        s.a = Math.max(0,Math.min(1,s.a+s.da)); if(s.a<=0||s.a>=1)s.da*=-1;
        s.x+=s.vx; s.y+=s.vy;
        if(s.y<-4){s.y=H+4;s.x=Math.random()*W;}
        if(s.x<-4||s.x>W+4)s.x=Math.random()*W;
        ctx.beginPath(); ctx.arc(s.x,s.y,s.r,0,Math.PI*2);
        ctx.fillStyle=`rgba(59,130,246,${(s.a*.6).toFixed(2)})`; ctx.fill();
      });
      requestAnimationFrame(draw);
    }
    draw(); window.addEventListener('resize', resize, {passive:true});
  }

  /* 2. Code rain in placeholders */
  function initCodeRain(ph) {
    const cv = document.createElement('canvas');
    const ctx = cv.getContext('2d');
    const chars = 'PYTHONDJANGORESTAPIPOSTGRESCELERYREDIS01';
    const fs = 10; let cols, drops;
    function resize() { cv.width=ph.offsetWidth; cv.height=ph.offsetHeight; cols=Math.floor(cv.width/fs); drops=Array(cols).fill(Math.random()*15|0); }
    function draw() {
      ctx.fillStyle='rgba(15,17,23,.15)'; ctx.fillRect(0,0,cv.width,cv.height);
      drops.forEach((y,i) => {
        ctx.fillStyle = Math.random()>.94 ? '#06b6d4' : 'rgba(59,130,246,.35)';
        ctx.font=`${fs}px monospace`;
        ctx.fillText(chars[Math.random()*chars.length|0], i*fs, y*fs);
        if(y*fs>cv.height&&Math.random()>.975) drops[i]=0;
        drops[i]++;
      });
      requestAnimationFrame(draw);
    }
    ph.prepend(cv); resize(); draw();
  }

  /* 3. Mouse spotlight + 3D tilt */
  function initCardFX() {
    document.querySelectorAll('.project-card').forEach(card => {
      card.addEventListener('mousemove', e => {
        const r = card.getBoundingClientRect();
        const x = e.clientX-r.left, y = e.clientY-r.top;
        card.style.setProperty('--mx', (x/r.width*100).toFixed(1)+'%');
        card.style.setProperty('--my', (y/r.height*100).toFixed(1)+'%');
        const dx=(x-r.width/2)/(r.width/2), dy=(y-r.height/2)/(r.height/2);
        card.style.transform=`perspective(900px) rotateY(${dx*6}deg) rotateX(${-dy*6}deg) translateY(-6px) scale(1.02)`;
      });
      card.addEventListener('mouseleave', () => { card.style.transform=''; });
    });
  }

  /* 4. Particle burst on click */
  function initParticles() {
    document.querySelectorAll('.project-card').forEach(card => {
      card.addEventListener('click', e => {
        for(let i=0;i<16;i++){
          const p=document.createElement('span');
          p.style.cssText=`position:fixed;left:${e.clientX}px;top:${e.clientY}px;width:6px;height:6px;border-radius:50%;pointer-events:none;z-index:9999;background:hsl(${200+Math.random()*40},90%,65%);transition:transform .6s ease,opacity .6s ease;transform:translate(-50%,-50%);opacity:1`;
          document.body.appendChild(p);
          const a=(Math.PI*2*i)/16, d=50+Math.random()*50;
          requestAnimationFrame(()=>{p.style.transform=`translate(${Math.cos(a)*d-3}px,${Math.sin(a)*d-3}px) scale(0)`;p.style.opacity='0';});
          setTimeout(()=>p.remove(),700);
        }
      });
    });
  }

  /* 5. Upgrade tech tags to icon badges */
  function upgradeTechTags() {
    document.querySelectorAll('.project-card .skill-tags').forEach(wrap => {
      const nw = document.createElement('div'); nw.className='tech-stack';
      wrap.querySelectorAll('.tag').forEach(tag => {
        const info = techInfo(tag.textContent.trim());
        const b = document.createElement('span');
        b.className='tech-badge'; b.title=info.label;
        b.style.cssText=`background:${info.color}16;color:${info.color};border-color:${info.color}30`;
        b.innerHTML=`<i class="${info.icon}"></i>${info.label}`;
        b.addEventListener('mouseenter',()=>{ b.style.background=info.color+'28'; b.style.transform='translateY(-2px) scale(1.07)'; b.style.boxShadow=`0 4px 14px ${info.color}38`; });
        b.addEventListener('mouseleave',()=>{ b.style.background=info.color+'16'; b.style.transform=''; b.style.boxShadow=''; });
        nw.appendChild(b);
      });
      wrap.replaceWith(nw);
    });
  }

  /* 6. Filter tabs */
  function initFilters() {
    const grid = document.querySelector('#projects .projects-grid');
    if (!grid) return;
    const techSet = new Set(['All']);
    document.querySelectorAll('.tech-badge').forEach(b => techSet.add(b.title));
    const bar = document.createElement('div'); bar.className='project-filters';
    [...techSet].slice(0,9).forEach(name => {
      const btn = document.createElement('button');
      btn.className='filter-btn'+(name==='All'?' active':''); btn.textContent=name;
      btn.addEventListener('click',()=>{
        bar.querySelectorAll('.filter-btn').forEach(b=>b.classList.remove('active')); btn.classList.add('active');
        document.querySelectorAll('.project-card').forEach(c => {
          const has = name==='All'||[...c.querySelectorAll('.tech-badge')].some(b=>b.title===name);
          c.style.opacity=has?'1':'0.18'; c.style.transform=has?'':'scale(0.95)'; c.style.pointerEvents=has?'':'none';
        });
      });
      bar.appendChild(btn);
    });
    grid.before(bar);
  }

  /* 7. Count label */
  function updateCount() {
    const n = document.querySelectorAll('.project-card').length;
    const el = document.getElementById('proj-count');
    if (el && n) el.innerHTML=`Showing <strong style="color:var(--primary)">${n}</strong> projects I've built`;
  }

  /* 8. Cycling placeholder icons */
  function cyclePlaceholderIcons() {
    const icons=['fas fa-code','fas fa-database','fas fa-server','fab fa-python','fab fa-docker','fas fa-plug'];
    document.querySelectorAll('.ph-icon').forEach((el,i)=>{
      let idx=(i+1)%icons.length;
      setInterval(()=>{
        el.style.opacity='0';
        setTimeout(()=>{ el.innerHTML=`<i class="${icons[idx%icons.length]}"></i>`; el.style.opacity='.8'; idx++; },280);
      }, 2400+i*600);
    });
  }

  /* 9. Scroll reveal for cards */
  function initReveal() {
    const cards=[...document.querySelectorAll('.project-card')];
    cards.forEach((c,i)=>{ c.style.opacity='0'; c.style.transform='translateY(32px)'; c.style.transition=`opacity .55s ${i*80}ms ease,transform .55s ${i*80}ms ease`; });
    const obs=new IntersectionObserver(es=>{
      es.forEach(e=>{ if(e.isIntersecting){ e.target.style.opacity='1'; e.target.style.transform=''; obs.unobserve(e.target); } });
    },{threshold:.08});
    cards.forEach(c=>obs.observe(c));
  }

  /* Boot */
  document.addEventListener('DOMContentLoaded',()=>{
    initStarfield();
    document.querySelectorAll('.project-placeholder').forEach(initCodeRain);
    upgradeTechTags();
    initFilters();
    updateCount();
    initCardFX();
    initParticles();
    initReveal();
    cyclePlaceholderIcons();

    // General scroll reveal
    document.querySelectorAll('.reveal').forEach(el=>{
      new IntersectionObserver(es=>{ es.forEach(e=>{ if(e.isIntersecting) e.target.classList.add('visible'); }); },{threshold:.1}).observe(el);
    });
  });
})();
