import './Pages.css';

const creators = [
  {
    name: 'Ayan Dutta',
    branch: 'Computer Science and Engineering',
    role: 'Project Lead',
    image:
      'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=900&q=80',
  },
  {
    name: 'Riya Das',
    branch: 'Information Technology',
    role: 'Risk Analysis',
    image:
      'https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=900&q=80',
  },
  {
    name: 'Nayan Roy',
    branch: 'Civil Engineering',
    role: 'Landslide Research',
    image:
      'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&w=900&q=80',
  },
];

export default function About() {
  return (
    <div className="about-page">
      <header className="about-hero">
        <div className="about-hero__text">
          <span className="about-badge">Landslide Monitoring</span>
          <h1>About Sathi</h1>
          <p>
            Sathi is a disaster-risk mapping platform created to help communities
            understand landslide and flood vulnerability with clarity and speed.
          </p>
        </div>

        <div className="about-hero__illustration" aria-label="Sathi illustration">
          <div className="illustration-card illustration-card--main">
            <div className="mini-map">
              <span className="map-dot map-dot--one" />
              <span className="map-dot map-dot--two" />
              <span className="map-dot map-dot--three" />
              <span className="map-line map-line--one" />
              <span className="map-line map-line--two" />
            </div>
          </div>
          <div className="illustration-card illustration-card--small">
            <span>Risk level</span>
            <strong>High</strong>
          </div>
          <div className="illustration-card illustration-card--badge">
            <span>Alerts</span>
            <strong>Live</strong>
          </div>
        </div>
      </header>

      <main className="about-content">
        <section className="feature-block">
          <div className="feature-number">01</div>
          <div>
            <h2>Our mission</h2>
            <p>
              We envision a safer and more prepared Northeast, where technology can identify danger before it becomes a disaster. Our mission is to turn early warnings into early action—helping people understand risks, prepare sooner, and respond better when floods and landslides threaten.
            </p>
          </div>
        </section>

        <section className="feature-block">
          <div className="feature-number">02</div>
          <div>
            <h2>Why This Matters</h2>
            <p>
              Early awareness can prevent loss of life and reduce damage to
              infrastructure. By identifying high-risk zones earlier, communities and
              authorities are better prepared for rainfall, evacuation, and response.
            </p>
          </div>
        </section>

        <section className="feature-block feature-block--wide">
          <div className="feature-number">03</div>
          <div>
            <h2>how it works</h2>
            <p>Sathi combines rainfall, soil, satellite, terrain, and historical disaster data. Its AI analyses these signals to detect changing risk patterns, identify vulnerable areas, and display them on an easy-to-understand map. The platform then provides timely insights and alerts to help communities and authorities make informed decisions when it matters most.</p>
          </div>
        </section>


      </main>

  
    </div>
  );
}
