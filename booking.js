// Booking Form Functionality
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('bookingForm');
    const summaryElements = {
        destination: document.getElementById('summaryDestination'),
        tourType: document.getElementById('summaryTourType'),
        dates: document.getElementById('summaryDates'),
        guests: document.getElementById('summaryGuests'),
        accommodation: document.getElementById('summaryAccommodation'),
        total: document.getElementById('summaryTotal')
    };

    // Price data
    const prices = {
        destinations: {
            'cape-coast': 89,
            'kakum': 120,
            'wli': 65,
            'labadi': 35,
            'ashanti': 75,
            'mole': 150
        },
        tourTypes: {
            'day-trip': 1,
            'weekend': 2,
            'week': 7,
            'custom': 3
        },
        accommodation: {
            'budget': 25,
            'standard': 50,
            'premium': 100,
            'luxury': 200
        }
    };

    // Check if destination was pre-selected from destinations page
    const selectedDestination = localStorage.getItem('selectedDestination');
    if (selectedDestination) {
        const destInfo = JSON.parse(selectedDestination);
        const destinationSelect = document.getElementById('destination');
        
        // Find matching option and select it
        for (let option of destinationSelect.options) {
            if (option.textContent.includes(destInfo.name)) {
                option.selected = true;
                updateSummary();
                break;
            }
        }
        
        // Clear the stored data
        localStorage.removeItem('selectedDestination');
    }

    // Set minimum date to today
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('checkIn').min = today;
    document.getElementById('checkOut').min = today;

    // Update check-out date when check-in changes
    document.getElementById('checkIn').addEventListener('change', function() {
        const checkInDate = new Date(this.value);
        checkInDate.setDate(checkInDate.getDate() + 1);
        document.getElementById('checkOut').min = checkInDate.toISOString().split('T')[0];
        
        // If check-out is before new minimum, update it
        const checkOutInput = document.getElementById('checkOut');
        if (checkOutInput.value && new Date(checkOutInput.value) <= new Date(this.value)) {
            checkOutInput.value = checkInDate.toISOString().split('T')[0];
        }
        
        updateSummary();
    });

    // Add event listeners to form elements
    const formElements = ['destination', 'tourType', 'checkIn', 'checkOut', 'adults', 'children', 'accommodation'];
    formElements.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.addEventListener('change', updateSummary);
        }
    });

    function updateSummary() {
        const formData = {
            destination: document.getElementById('destination').value,
            tourType: document.getElementById('tourType').value,
            checkIn: document.getElementById('checkIn').value,
            checkOut: document.getElementById('checkOut').value,
            adults: parseInt(document.getElementById('adults').value) || 1,
            children: parseInt(document.getElementById('children').value) || 0,
            accommodation: document.getElementById('accommodation').value
        };

        // Update destination
        if (formData.destination) {
            const destinationText = document.getElementById('destination').options[document.getElementById('destination').selectedIndex].textContent;
            summaryElements.destination.textContent = destinationText.split(' - ')[0];
        } else {
            summaryElements.destination.textContent = 'Not selected';
        }

        // Update tour type
        if (formData.tourType) {
            const tourTypeText = document.getElementById('tourType').options[document.getElementById('tourType').selectedIndex].textContent;
            summaryElements.tourType.textContent = tourTypeText;
        } else {
            summaryElements.tourType.textContent = 'Not selected';
        }

        // Update dates
        if (formData.checkIn && formData.checkOut) {
            const checkIn = new Date(formData.checkIn);
            const checkOut = new Date(formData.checkOut);
            const nights = Math.ceil((checkOut - checkIn) / (1000 * 60 * 60 * 24));
            summaryElements.dates.textContent = `${formatDate(checkIn)} - ${formatDate(checkOut)} (${nights} nights)`;
        } else {
            summaryElements.dates.textContent = 'Not selected';
        }

        // Update guests
        const totalGuests = formData.adults + formData.children;
        if (totalGuests > 0) {
            let guestText = `${formData.adults} adult${formData.adults > 1 ? 's' : ''}`;
            if (formData.children > 0) {
                guestText += `, ${formData.children} child${formData.children > 1 ? 'ren' : ''}`;
            }
            summaryElements.guests.textContent = guestText;
        } else {
            summaryElements.guests.textContent = 'Not selected';
        }

        // Update accommodation
        if (formData.accommodation) {
            const accommodationText = document.getElementById('accommodation').options[document.getElementById('accommodation').selectedIndex].textContent;
            summaryElements.accommodation.textContent = accommodationText;
        } else {
            summaryElements.accommodation.textContent = 'Not selected';
        }

        // Calculate total price
        let totalPrice = calculateTotal(formData);
        summaryElements.total.textContent = `$${totalPrice}`;
    }

    function calculateTotal(formData) {
        let total = 0;

        // Base destination price
        if (formData.destination && prices.destinations[formData.destination]) {
            const basePrice = prices.destinations[formData.destination];
            const totalGuests = formData.adults + (formData.children * 0.5); // Children at half price
            total += basePrice * totalGuests;
        }

        // Tour type multiplier
        if (formData.tourType && prices.tourTypes[formData.tourType]) {
            total *= prices.tourTypes[formData.tourType];
        }

        // Accommodation costs
        if (formData.accommodation && formData.checkIn && formData.checkOut) {
            const checkIn = new Date(formData.checkIn);
            const checkOut = new Date(formData.checkOut);
            const nights = Math.ceil((checkOut - checkIn) / (1000 * 60 * 60 * 24));
            
            if (nights > 0 && prices.accommodation[formData.accommodation]) {
                const accommodationCost = prices.accommodation[formData.accommodation] * nights;
                total += accommodationCost;
            }
        }

        return Math.round(total);
    }

    function formatDate(date) {
        return date.toLocaleDateString('en-US', { 
            month: 'short', 
            day: 'numeric', 
            year: 'numeric' 
        });
    }

    // Form submission
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        
        // Basic form validation
        const requiredFields = ['destination', 'tourType', 'checkIn', 'checkOut', 'adults', 'accommodation', 'firstName', 'lastName', 'email', 'phone', 'country'];
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
        const email = document.getElementById('email').value;
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            document.getElementById('email').style.borderColor = '#ff4444';
            isValid = false;
        }

        // Date validation
        const checkIn = new Date(document.getElementById('checkIn').value);
        const checkOut = new Date(document.getElementById('checkOut').value);
        if (checkOut <= checkIn) {
            document.getElementById('checkOut').style.borderColor = '#ff4444';
            isValid = false;
        }

        if (isValid) {
            // Simulate booking process
            const submitButton = form.querySelector('button[type="submit"]');
            const originalText = submitButton.innerHTML;
            
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
            submitButton.disabled = true;
            
            setTimeout(() => {
                alert('Booking submitted successfully! You will receive a confirmation email shortly.');
                
                // Reset form
                form.reset();
                updateSummary();
                
                // Reset button
                submitButton.innerHTML = originalText;
                submitButton.disabled = false;
                
                // Redirect to confirmation page or home
                window.location.href = 'index.html';
            }, 2000);
        } else {
            alert('Please fill in all required fields correctly.');
        }
    });

    // Initialize summary on page load
    updateSummary();
});