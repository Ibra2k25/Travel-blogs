// Contact Form and FAQ Functionality
document.addEventListener('DOMContentLoaded', () => {
    const contactForm = document.getElementById('contactForm');
    const faqItems = document.querySelectorAll('.faq-item');

    // FAQ Accordion Functionality
    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');
        
        question.addEventListener('click', () => {
            const isActive = item.classList.contains('active');
            
            // Close all FAQ items
            faqItems.forEach(faqItem => {
                faqItem.classList.remove('active');
            });
            
            // Open clicked item if it wasn't active
            if (!isActive) {
                item.classList.add('active');
            }
        });
    });

    // Contact Form Submission
    contactForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        // Get form data
        const formData = {
            name: document.getElementById('name').value,
            email: document.getElementById('email').value,
            phone: document.getElementById('phone').value,
            subject: document.getElementById('subject').value,
            message: document.getElementById('message').value,
            newsletter: document.getElementById('newsletter').checked
        };

        // Basic validation
        const requiredFields = ['name', 'email', 'subject', 'message'];
        let isValid = true;

        requiredFields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (!field.value.trim()) {
                field.style.borderColor = '#ff4444';
                isValid = false;
            } else {
                field.style.borderColor = 'rgba(255, 255, 255, 0.2)';
            }
        });

        // Email validation
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(formData.email)) {
            document.getElementById('email').style.borderColor = '#ff4444';
            isValid = false;
        }

        if (isValid) {
            // Simulate form submission
            const submitButton = contactForm.querySelector('button[type="submit"]');
            const originalText = submitButton.innerHTML;
            
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
            submitButton.disabled = true;
            
            setTimeout(() => {
                alert('Thank you for your message! We will get back to you within 24 hours.');
                
                // Reset form
                contactForm.reset();
                
                // Reset button
                submitButton.innerHTML = originalText;
                submitButton.disabled = false;
                
                // Reset field borders
                requiredFields.forEach(fieldId => {
                    document.getElementById(fieldId).style.borderColor = 'rgba(255, 255, 255, 0.2)';
                });
                
            }, 2000);
        } else {
            alert('Please fill in all required fields correctly.');
        }
    });

    // Form field focus effects
    const formFields = contactForm.querySelectorAll('input, select, textarea');
    formFields.forEach(field => {
        field.addEventListener('focus', () => {
            field.style.borderColor = '#9acd32';
            field.style.transform = 'scale(1.02)';
        });

        field.addEventListener('blur', () => {
            if (field.value.trim()) {
                field.style.borderColor = 'rgba(255, 255, 255, 0.3)';
            } else {
                field.style.borderColor = 'rgba(255, 255, 255, 0.2)';
            }
            field.style.transform = 'scale(1)';
        });
    });

    // Social links hover effects
    const socialLinks = document.querySelectorAll('.social-link');
    socialLinks.forEach(link => {
        link.addEventListener('mouseenter', () => {
            link.style.transform = 'translateY(-5px) scale(1.1)';
        });

        link.addEventListener('mouseleave', () => {
            link.style.transform = 'translateY(0) scale(1)';
        });
    });

    // Animate contact items on scroll
    const contactItems = document.querySelectorAll('.contact-item');
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateX(0)';
            }
        });
    }, observerOptions);

    contactItems.forEach((item, index) => {
        item.style.opacity = '0';
        item.style.transform = 'translateX(-30px)';
        item.style.transition = `opacity 0.6s ease ${index * 0.1}s, transform 0.6s ease ${index * 0.1}s`;
        observer.observe(item);
    });

    // Auto-fill form from URL parameters (if coming from other pages)
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('subject')) {
        document.getElementById('subject').value = urlParams.get('subject');
    }
    if (urlParams.has('message')) {
        document.getElementById('message').value = urlParams.get('message');
    }
});