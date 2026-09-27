import { useRef, useState } from 'react';
import emailjs from '@emailjs/browser';
import './Pages.css';

const serviceId = import.meta.env.VITE_EMAILJS_SERVICE_ID;
const templateId = import.meta.env.VITE_EMAILJS_TEMPLATE_ID;
const publicKey = import.meta.env.VITE_EMAILJS_PUBLIC_KEY;

export default function Contact() {
  const formRef = useRef(null);
  const [status, setStatus] = useState({ type: 'idle', message: '' });

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!serviceId || !templateId || !publicKey) {
      setStatus({
        type: 'error',
        message: 'EmailJS is not configured yet. Add your keys to the .env file.',
      });
      return;
    }

    try {
      setStatus({ type: 'loading', message: 'Sending your message...' });

      await emailjs.sendForm(serviceId, templateId, formRef.current, {
        publicKey,
      });

      setStatus({
        type: 'success',
        message: 'Your message has been sent successfully.',
      });
      formRef.current.reset();
    } catch (error) {
      console.error('EmailJS error:', error);
      setStatus({
        type: 'error',
        message: 'Something went wrong. Please try again later.',
      });
    }
  };

  return (
    <div className="contact-page">
      <div className="contact-intro">
        <span className="section-kicker">Contact</span>
        <h1>Get in touch</h1>
        <p>
          Have questions, feedback, or want to contribute data? Reach out to us.
        </p>
      </div>

      <div className="contact-shell">
        <aside className="contact-panel">
          <h2>Let’s build safer communities</h2>
          <p>
            We’re working to improve landslide awareness, early warning, and
            climate resilience through accessible risk information.
          </p>

          <div className="contact-points">
            <div>
              <strong>Email</strong>
              <span>helplinesathi@gmail.com</span>
            </div>
            <div>
              <strong>phone number</strong>
              <span>7099449544</span>
            </div>
          </div>
        </aside>

        <form ref={formRef} className="contact-form" onSubmit={handleSubmit}>
          <div className="contact-form__group">
            <label className="contact-form__label" htmlFor="contact-name">
              Name
            </label>
            <input
              id="contact-name"
              className="contact-form__input"
              type="text"
              name="name"
              placeholder="Your name"
              required
            />
          </div>

          <div className="contact-form__group">
            <label className="contact-form__label" htmlFor="contact-email">
              Email
            </label>
            <input
              id="contact-email"
              className="contact-form__input"
              type="email"
              name="email"
              placeholder="you@example.com"
              required
            />
          </div>

          <div className="contact-form__group">
            <label className="contact-form__label" htmlFor="contact-message">
              Message
            </label>
            <textarea
              id="contact-message"
              className="contact-form__textarea"
              name="message"
              placeholder="How can we help?"
              required
            />
          </div>

          <button
            className="contact-form__submit"
            type="submit"
            disabled={status.type === 'loading'}
          >
            {status.type === 'loading' ? 'Sending...' : 'Send Message'}
          </button>

          {status.message && (
            <p className={`contact-status contact-status--${status.type}`}>
              {status.message}
            </p>
          )}
        </form>
      </div>
    </div>
  );
}
