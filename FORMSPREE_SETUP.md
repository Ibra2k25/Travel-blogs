# 🔧 Formspree Setup Guide for Discover Ghana Website

This guide will help you set up Formspree form handling for all the contact and booking forms on the Discover Ghana website.

## 📋 What is Formspree?

Formspree is a form backend service that allows you to handle form submissions without writing server-side code. It's perfect for static websites like ours.

## 🚀 Quick Setup Steps

### 1. Create a Formspree Account

1. Go to [formspree.io](https://formspree.io)
2. Sign up for a free account
3. Verify your email address

### 2. Create Forms

You'll need to create **5 separate forms** in Formspree for different purposes:

#### Form 1: Main Booking Form
- **Purpose**: Main booking requests from booking.html
- **Form Name**: "Ghana Booking Requests"
- **Expected Fields**: firstName, lastName, email, phone, country, age, checkIn, checkOut, duration, guests, accommodation, package, destinations, interests, budget, dietary, accessibility, message, newsletter, terms

#### Form 2: General Inquiry Form
- **Purpose**: General questions from contact.html
- **Form Name**: "General Inquiries"
- **Expected Fields**: name, email, phone, subject, message

#### Form 3: Quick Booking Form
- **Purpose**: Quick booking requests from contact.html
- **Form Name**: "Quick Booking Requests"
- **Expected Fields**: name, email, phone, travelers, dates, budget, interests

#### Form 4: Custom Tour Form
- **Purpose**: Custom tour requests from contact.html
- **Form Name**: "Custom Tour Requests"
- **Expected Fields**: name, email, duration, group, interests, description

#### Form 5: Business Inquiries Form
- **Purpose**: Partnership and business inquiries from contact.html
- **Form Name**: "Business Inquiries"
- **Expected Fields**: name, email, company, type, message

#### Form 6: Newsletter Form
- **Purpose**: Newsletter subscriptions (used across all pages)
- **Form Name**: "Newsletter Subscriptions"
- **Expected Fields**: email

### 3. Get Your Form IDs

After creating each form in Formspree, you'll get a unique form ID that looks like this: `xvgpkdlr`

### 4. Update the HTML Files

Replace the placeholder form IDs in your HTML files:

#### In `booking.html`:
```html
<!-- Find this line: -->
<form action="https://formspree.io/f/YOUR_FORM_ID" method="POST" class="booking-form" id="bookingForm">

<!-- Replace YOUR_FORM_ID with your actual Formspree ID: -->
<form action="https://formspree.io/f/xvgpkdlr" method="POST" class="booking-form" id="bookingForm">
```

#### In `contact.html`:
Replace **4 different form IDs**:

```html
<!-- General Inquiry Form -->
<form action="https://formspree.io/f/YOUR_GENERAL_FORM_ID" method="POST" class="contact-form">
<!-- Replace with: -->
<form action="https://formspree.io/f/xabcdefg" method="POST" class="contact-form">

<!-- Quick Booking Form -->
<form action="https://formspree.io/f/YOUR_BOOKING_FORM_ID" method="POST" class="contact-form">
<!-- Replace with: -->
<form action="https://formspree.io/f/xhijklmn" method="POST" class="contact-form">

<!-- Custom Tour Form -->
<form action="https://formspree.io/f/YOUR_CUSTOM_FORM_ID" method="POST" class="contact-form">
<!-- Replace with: -->
<form action="https://formspree.io/f/xopqrstu" method="POST" class="contact-form">

<!-- Business Form -->
<form action="https://formspree.io/f/YOUR_BUSINESS_FORM_ID" method="POST" class="contact-form">
<!-- Replace with: -->
<form action="https://formspree.io/f/xvwxyzab" method="POST" class="contact-form">
```

#### In ALL pages with Newsletter Forms:
```html
<!-- Find this in index.html, destinations.html, packages.html, culture.html, contact.html: -->
<form action="https://formspree.io/f/YOUR_FORM_ID" method="POST" class="newsletter-form">

<!-- Replace with: -->
<form action="https://formspree.io/f/xnewsltr" method="POST" class="newsletter-form">
```

## 📧 Form Configuration in Formspree

### 1. Email Settings

For each form, configure:
- **Reply-to**: Set to the user's email field
- **Email Subject**: Use the `_subject` hidden field values
- **CC/BCC**: Add your team emails if needed

### 2. Spam Protection

Enable Formspree's built-in spam protection:
- Enable reCAPTCHA (optional)
- Set up honeypot fields
- Configure spam filtering

### 3. Auto-Responses

Set up automatic confirmation emails for users:

#### For Booking Forms:
```
Subject: Booking Request Received - Discover Ghana

Dear {{name}},

Thank you for your interest in visiting Ghana! We've received your booking request and will get back to you within 24 hours with a personalized itinerary.

Your request details:
- Package: {{package}}
- Travelers: {{guests}}
- Dates: {{checkIn}} to {{checkOut}}

Best regards,
The Discover Ghana Team
```

#### For General Inquiries:
```
Subject: Message Received - Discover Ghana

Hi {{name}},

Thanks for contacting us! We've received your message about {{subject}} and will respond within 24 hours.

Best regards,
The Discover Ghana Team
```

## 🔧 Advanced Configuration

### 1. Custom Thank You Pages

Create custom thank you pages and update the `_next` hidden fields:

```html
<input type="hidden" name="_next" value="https://yourdomain.com/thank-you-booking.html">
```

### 2. Form Validation

Formspree handles server-side validation, but our JavaScript provides client-side validation for better UX.

### 3. File Uploads (Optional)

If you want to allow file uploads later:

```html
<input type="file" name="documents" accept=".pdf,.doc,.docx">
```

### 4. Webhook Integration

Set up webhooks to integrate with:
- CRM systems
- Email marketing platforms
- Slack notifications
- Custom analytics

## 📊 Form Analytics

Monitor your forms in the Formspree dashboard:
- Submission counts
- Spam detection stats
- Response times
- Popular form fields

## 🔒 Security Features

Formspree provides:
- HTTPS encryption
- Spam filtering
- Rate limiting
- GDPR compliance tools

## 🆓 Pricing

**Free Plan**: 50 submissions/month
**Paid Plans**: Starting at $10/month for unlimited submissions

## ✅ Testing Your Forms

1. **Test locally**: Submit forms to verify they work
2. **Check email delivery**: Ensure emails arrive in your inbox
3. **Test validation**: Try submitting incomplete forms
4. **Mobile testing**: Test forms on mobile devices
5. **Cross-browser**: Test in different browsers

## 🐛 Troubleshooting

### Common Issues:

1. **Form not submitting**
   - Check the form action URL
   - Verify form ID is correct
   - Ensure form method is POST

2. **Emails not arriving**
   - Check spam folder
   - Verify email configuration in Formspree
   - Check sender reputation

3. **Validation errors**
   - Ensure required fields are properly named
   - Check JavaScript validation logic
   - Verify HTML form attributes

### Support Resources:

- [Formspree Documentation](https://help.formspree.io/)
- [Formspree Support](https://formspree.io/contact)
- [GitHub Issues](https://github.com/formspree/formspree/issues)

## 🔄 Backup Options

Consider these alternatives if Formspree doesn't meet your needs:
- **Netlify Forms** (if hosting on Netlify)
- **Getform**
- **Form.io**
- **EmailJS**
- **Custom backend** (Node.js, PHP, etc.)

## 📝 Form Field Reference

### Main Booking Form Fields:
- `firstName`, `lastName`, `email`, `phone`
- `country`, `age`, `checkIn`, `checkOut`
- `duration`, `guests`, `accommodation`
- `package`, `destinations[]`, `interests[]`
- `budget`, `dietary`, `accessibility`
- `message`, `newsletter`, `terms`

### Contact Form Fields:
- `name`, `email`, `phone`, `subject`, `message`
- `travelers`, `dates`, `budget`, `interests`
- `duration`, `group`, `description`
- `company`, `type`

---

## 🎉 You're All Set!

Once you've completed these steps, your Ghana travel website will have fully functional contact and booking forms powered by Formspree. Visitors can now easily inquire about trips and make booking requests!

**Need Help?** Contact the development team or refer to the Formspree documentation for additional support.