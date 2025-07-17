// Destination Filter Functionality
document.addEventListener('DOMContentLoaded', () => {
    const filterButtons = document.querySelectorAll('.filter-btn');
    const destinationCards = document.querySelectorAll('.destination-card');

    // Filter functionality
    filterButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remove active class from all buttons
            filterButtons.forEach(btn => btn.classList.remove('active'));
            
            // Add active class to clicked button
            button.classList.add('active');
            
            const filterValue = button.getAttribute('data-filter');
            
            // Filter destination cards
            destinationCards.forEach(card => {
                const cardCategory = card.getAttribute('data-category');
                
                if (filterValue === 'all' || cardCategory === filterValue) {
                    card.style.display = 'block';
                    card.style.opacity = '0';
                    card.style.transform = 'translateY(20px)';
                    
                    // Animate in
                    setTimeout(() => {
                        card.style.opacity = '1';
                        card.style.transform = 'translateY(0)';
                    }, 100);
                } else {
                    card.style.opacity = '0';
                    card.style.transform = 'translateY(-20px)';
                    
                    setTimeout(() => {
                        card.style.display = 'none';
                    }, 300);
                }
            });
        });
    });

    // Book Now button functionality
    const bookButtons = document.querySelectorAll('.destination-card .btn-primary');
    bookButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Get destination name from the card
            const card = button.closest('.destination-card');
            const destinationName = card.querySelector('h3').textContent;
            
            // Store destination info in localStorage for booking page
            const destinationInfo = {
                name: destinationName,
                price: card.querySelector('.price').textContent,
                category: card.getAttribute('data-category')
            };
            
            localStorage.setItem('selectedDestination', JSON.stringify(destinationInfo));
            
            // Navigate to booking page
            window.location.href = 'booking.html';
        });
    });

    // Add scroll animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe destination cards for scroll animations
    destinationCards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(50px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });

    // CTA button functionality
    const ctaButton = document.querySelector('.cta .btn-primary');
    if (ctaButton) {
        ctaButton.addEventListener('click', () => {
            window.location.href = 'booking.html';
        });
    }
});