// Extra JavaScript for trustguard documentation

document.addEventListener('DOMContentLoaded', function() {
  // Add copy buttons to code blocks
  const codeBlocks = document.querySelectorAll('pre code');
  codeBlocks.forEach((block) => {
    const button = document.createElement('button');
    button.className = 'md-clipboard md-icon';
    button.title = 'Copy to clipboard';
    button.setAttribute('aria-label', 'Copy to clipboard');
    button.innerHTML = '<svg viewBox="0 0 24 24"><path d="M19,21H8V7H19M19,5H8A2,2 0 0,0 6,7V21A2,2 0 0,0 8,23H19A2,2 0 0,0 21,21V7A2,2 0 0,0 19,5M16,1H4A2,2 0 0,0 2,3V17H4V3H16V1Z"></path></svg>';
    
    block.parentNode.insertBefore(button, block);
    
    button.addEventListener('click', () => {
      const code = block.innerText;
      navigator.clipboard.writeText(code).then(() => {
        button.classList.add('md-clipboard--success');
        button.innerHTML = '<svg viewBox="0 0 24 24"><path d="M21,7L9,19L3.5,13.5L4.91,12.09L9,16.17L19.59,5.59L21,7Z"></path></svg>';
        setTimeout(() => {
          button.classList.remove('md-clipboard--success');
          button.innerHTML = '<svg viewBox="0 0 24 24"><path d="M19,21H8V7H19M19,5H8A2,2 0 0,0 6,7V21A2,2 0 0,0 8,23H19A2,2 0 0,0 21,21V7A2,2 0 0,0 19,5M16,1H4A2,2 0 0,0 2,3V17H4V3H16V1Z"></path></svg>';
        }, 2000);
      });
    });
  });
  
  // Add version selector if needed
  const versionSelect = document.querySelector('.md-version');
  if (versionSelect) {
    versionSelect.addEventListener('change', (e) => {
      window.location.href = e.target.value;
    });
  }
  
  // Track search events
  const searchInput = document.querySelector('.md-search__input');
  if (searchInput) {
    searchInput.addEventListener('keyup', (e) => {
      if (e.key === 'Enter') {
        console.log('Search:', searchInput.value);
        // Add analytics tracking here
      }
    });
  }
});

// Smooth scroll for anchor links
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
