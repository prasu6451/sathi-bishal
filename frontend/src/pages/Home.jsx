import MapView from '../components/MapView';
import { GoShieldCheck } from "react-icons/go";
import { FaBell, FaFileContract } from "react-icons/fa6";
import { Link } from 'react-router-dom';
import './home.css'


export default function Home() {
  return (
    <div className='above-home-container'>
      <div className='home-container'>
        <div className='left'>
          <span ><GoShieldCheck /> <span>Ai-powered early warning system </span></span>

          <div className='homepage-Texts'>
            <h1>Predict. Prepare. <br /> <span>Protect Lives.</span></h1>

            <p>Ai powered real time moitoring and prediction platform for floods, landslides, and other natural disasters across the North Eastern Region. Early alerts, live insights, and community reporting for a safter tomorrow.</p>

          </div>

          <div className="buttons">

            <Link className='live-map-btn button' to={'/liveMap'}>
              <FaBell />
              <span>  View Live Map</span>
            </Link>


            <Link to={'/dashboard'} className='explore-dashboard-btn button'>
              Explore Dashboard
            </Link>

            
            <Link to={'/report'} className='explore-dashboard-btn button'>
            <FaFileContract />
              Ground Report
            </Link>
          </div>
        </div>
         <Link to={'/livemap'}  className='right' >
          <MapView version='home'></MapView>
        </Link>
      

      </div>
    </div>
  );
}
