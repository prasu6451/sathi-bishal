import { useState } from 'react';
import { Link, NavLink } from 'react-router-dom';
import ProfileModal from './ProfileModal';
import './Header.css';

export default function Header({ isLoggedIn, onLogout }) {
  const [showProfile, setShowProfile] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <>
      <header className="header">
        <div className="header__inner">
          <Link to="/" className="header__logo">
            <img src="sathi-logo.png" alt="logo" />
            <img src="/sathi-word-logo.png" alt="Sathi" />
          </Link>

          <div className="header__right">
            {/* Desktop nav */}
            <nav className="header__nav">
              <NavLink
                to="/"
                className={({ isActive }) =>
                  `header__nav-link${isActive ? ' active' : ''}`
                }
              >
                home
              </NavLink>

              <NavLink
                to="/liveMap"
                className={({ isActive }) =>
                  `header__nav-link${isActive ? ' active' : ''}`
                }
              >
                live map
              </NavLink>

              <NavLink
                to="/dashboard"
                className={({ isActive }) =>
                  `header__nav-link${isActive ? ' active' : ''}`
                }
              >
                Dashboard
              </NavLink>

              <NavLink
                to="/report"
                className={({ isActive }) =>
                  `header__nav-link${isActive ? ' active' : ''}`
                }
              >
                Report
              </NavLink>

              <NavLink
                to="/disaster"
                className={({ isActive }) =>
                  `header__nav-link${isActive ? ' active' : ''}`
                }
              >
                Disaster AI
              </NavLink>

              <NavLink
                to="/sathi"
                className={({ isActive }) =>
                  `header__nav-link${isActive ? ' active' : ''}`
                }
              >
                Sathi Help
              </NavLink>

              <NavLink
                to="/about"
                className={({ isActive }) =>
                  `header__nav-link${isActive ? ' active' : ''}`
                }
              >
                About
              </NavLink>
              <NavLink
                to="/contact"
                className={({ isActive }) =>
                  `header__nav-link${isActive ? ' active' : ''}`
                }
              >
                Contact
              </NavLink>


            </nav>



            {/* Mobile hamburger */}
            <button
              className="header__hamburger"
              onClick={() => setMobileOpen((v) => !v)}
              aria-label="Toggle navigation"
            >
              {mobileOpen ? (
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              ) : (
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="3" y1="6" x2="21" y2="6" />
                  <line x1="3" y1="12" x2="21" y2="12" />
                  <line x1="3" y1="18" x2="21" y2="18" />
                </svg>
              )}
            </button>
          </div>
        </div>
      </header>

      {/* Mobile nav dropdown */}
      {mobileOpen && (
        <nav className="header__mobile-nav">
          <NavLink
            to="/"
            className={({ isActive }) =>
              `header__nav-link${isActive ? ' active' : ''}`
            }
            onClick={() => setMobileOpen(false)}
          >
            home
          </NavLink>
          <NavLink
            to="/liveMap"
            className={({ isActive }) =>
              `header__nav-link${isActive ? ' active' : ''}`
            }
            onClick={() => setMobileOpen(false)}
          >
            live map
          </NavLink>
          <NavLink
            to="/dashboard"
            className={({ isActive }) =>
              `header__nav-link${isActive ? ' active' : ''}`
            }
            onClick={() => setMobileOpen(false)}
          >
            Dashboard
          </NavLink>
          <NavLink
            to="/report"
            className={({ isActive }) =>
              `header__nav-link${isActive ? ' active' : ''}`
            }
            onClick={() => setMobileOpen(false)}
          >
            Report
          </NavLink>
          <NavLink
            to="/disaster"
            className={({ isActive }) =>
              `header__nav-link${isActive ? ' active' : ''}`
            }
            onClick={() => setMobileOpen(false)}
          >
            Disaster AI
          </NavLink>
          <NavLink
            to="/sathi"
            className={({ isActive }) =>
              `header__nav-link${isActive ? ' active' : ''}`
            }
            onClick={() => setMobileOpen(false)}
          >
            Sathi Help
          </NavLink>
          <NavLink
            to="/admin"
            className={({ isActive }) =>
              `header__nav-link${isActive ? ' active' : ''}`
            }
            onClick={() => setMobileOpen(false)}
          >
            Admin
          </NavLink>
          <NavLink
            to="/about"
            className={({ isActive }) =>
              `header__nav-link${isActive ? ' active' : ''}`
            }
            onClick={() => setMobileOpen(false)}
          >
            About
          </NavLink>

          <NavLink
            to="/contact"
            className={({ isActive }) =>
              `header__nav-link${isActive ? ' active' : ''}`
            }
            onClick={() => setMobileOpen(false)}
          >
            Contact
          </NavLink>
        </nav>
      )}

      {/* Profile modal */}
      {showProfile && (
        <ProfileModal
          isLoggedIn={isLoggedIn}
          onClose={() => setShowProfile(false)}
          onLogout={onLogout}
        />
      )}
    </>
  );
}
