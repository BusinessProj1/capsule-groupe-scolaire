document.addEventListener('DOMContentLoaded', () => {
    // Reveal Animations on Scroll
    const reveals = document.querySelectorAll('.reveal');

    const revealOnScroll = () => {
        const windowHeight = window.innerHeight;
        const elementVisible = 100;

        reveals.forEach((reveal) => {
            const elementTop = reveal.getBoundingClientRect().top;
            if (elementTop < windowHeight - elementVisible) {
                reveal.classList.add('active');
            }
        });
    };

    window.addEventListener('scroll', revealOnScroll);
    revealOnScroll(); // Trigger once on load

    // --- Counter Animation ---
    const counters = document.querySelectorAll('.counter');
    const animateCounter = (counter) => {
        const target = +counter.getAttribute('data-target');
        const suffix = counter.getAttribute('data-suffix') || '';
        const duration = 600; // ms
        const increment = target / (duration / 16); // 60fps
        
        let current = 0;
        const updateCounter = () => {
            current += increment;
            if (current < target) {
                counter.innerText = Math.ceil(current) + suffix;
                requestAnimationFrame(updateCounter);
            } else {
                counter.innerText = target + suffix;
            }
        };
        updateCounter();
    };

    const counterObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounter(entry.target);
                observer.unobserve(entry.target); // Animate only once
            }
        });
    }, { threshold: 0.5 });

    counters.forEach(counter => {
        counterObserver.observe(counter);
    });

    // --- Comment System using LocalStorage ---
    const commentForm = document.getElementById('comment-form');
    const commentsList = document.getElementById('comments-list');

    if (commentForm && commentsList) {
        // Load existing comments
        const loadComments = () => {
            let comments = JSON.parse(localStorage.getItem('plateforme_edu_comments'));
            
            if (!comments) {
                comments = [];
                localStorage.setItem('plateforme_edu_comments', JSON.stringify(comments));
            }
            
            // Remove dummy comment if it exists from previous sessions
            if (comments.some(c => c.name === "Marie P.")) {
                comments = comments.filter(c => c.name !== "Marie P.");
                localStorage.setItem('plateforme_edu_comments', JSON.stringify(comments));
            }

            commentsList.innerHTML = '';
            
            comments.forEach(comment => {
                const card = document.createElement('div');
                card.className = 'card reveal active'; // active directly so it shows up
                card.innerHTML = `
                    <div class="temoignage-stars">★★★★★</div>
                    <p class="temoignage-msg">"${comment.text}"</p>
                    <div class="temoignage-auteur">
                        <div class="avatar">${comment.avatar}</div>
                        <div>
                            <b style="font-size: 1.1rem;">${comment.name}</b><br>
                            <small style="color: var(--text-muted); font-weight: 500;">${comment.role}</small>
                        </div>
                    </div>
                `;
                commentsList.appendChild(card);
            });
        };

        loadComments();

        // Handle submit
        commentForm.addEventListener('submit', (e) => {
            e.preventDefault();
            
            const nameInput = document.getElementById('comment-name').value;
            const roleInput = document.getElementById('comment-role').value;
            const textInput = document.getElementById('comment-text').value;
            
            if(!nameInput || !textInput) return;

            const newComment = {
                name: nameInput,
                role: roleInput || 'Élève / Parent',
                text: textInput,
                avatar: nameInput.charAt(0).toUpperCase()
            };

            const comments = JSON.parse(localStorage.getItem('plateforme_edu_comments')) || [];
            comments.unshift(newComment); // add to top
            
            localStorage.setItem('plateforme_edu_comments', JSON.stringify(comments));
            
            // Reset form and reload
            commentForm.reset();
            loadComments();
            
            alert('Votre témoignage a été ajouté avec succès !');
        });
    }

    // --- WhatsApp Booking Form ---
    const bookingForm = document.getElementById('bookingForm');
    if (bookingForm) {
        bookingForm.addEventListener('submit', (e) => {
            e.preventDefault();
            
            const nom = document.getElementById('wa-nom').value;
            const matiere = document.getElementById('wa-matiere').value;
            
            // Handle radio buttons
            const formatEl = document.querySelector('input[name="format"]:checked');
            const format = formatEl ? formatEl.value : 'Non spécifié';
            
            const details = document.getElementById('wa-details').value || 'Aucun détail supplémentaire';
            
            const message = `Bonjour, je souhaite effectuer une réservation de cours de Mathématiques :\n\n` +
                            `*Nom complet* : ${nom}\n` +
                            `*Niveau scolaire* : ${matiere}\n` +
                            `*Format* : ${format}\n` +
                            `*Détails* : ${details}`;
            
            // Encode message for URL
            const encodedMessage = encodeURIComponent(message);
            // Replace with the user's WhatsApp number
            const whatsappNumber = '212613214968'; 
            
            const whatsappUrl = `https://wa.me/${whatsappNumber}?text=${encodedMessage}`;
            
            window.open(whatsappUrl, '_blank');
        });
    }

    // --- Tab Switching for Courses Page ---
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class from all buttons and contents
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            // Add active class to clicked button and corresponding content
            btn.classList.add('active');
            const tabId = btn.getAttribute('data-tab');
            document.getElementById(`${tabId}-tab`).classList.add('active');

            // Re-trigger reveal animations for the new tab
            const newTabContent = document.getElementById(`${tabId}-tab`);
            const revealsInTab = newTabContent.querySelectorAll('.reveal');
            revealsInTab.forEach(reveal => {
                reveal.classList.remove('active');
                setTimeout(() => {
                    reveal.classList.add('active');
                }, 50);
            });
        });
    });
});
