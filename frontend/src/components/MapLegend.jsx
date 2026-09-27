export default function MapLegend() {
  return (
    <div className="map-legend">
      <div className="map-legend__title">Risk Categories</div>
      <div className="map-legend__item">
        <span className="map-legend__dot map-legend__dot--critical" />
        Critical Risk
      </div>
      <div className="map-legend__item">
        <span className="map-legend__dot map-legend__dot--high" />
        High Risk
      </div>
      <div className="map-legend__item">
        <span className="map-legend__dot map-legend__dot--flood-plain" />
        Flood Plain Risk
      </div>
      <div className="map-legend__item">
        <span className="map-legend__dot map-legend__dot--low" />
        Low Risk
      </div>
    </div>
  );
}
