import React from "react";

function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="footer">
      <div className="footer-content">
        <p className="footer-disclaimer">
          This is an educational project. The predictive models are for
          informational purposes only and not a substitute for professional
          medical advice.
        </p>
        <p className="footer-sources">
          Dataset sources proudly acknowledged:
          <a
            href="https://www.kaggle.com/"
            target="_blank"
            rel="noopener noreferrer"
          >
            {" "}
            Kaggle{" "}
          </a>
          &
          <a
            href="https://archive.ics.uci.edu/ml/index.php"
            target="_blank"
            rel="noopener noreferrer"
          >
            {" "}
            UCI Machine Learning Repository
          </a>
          .
        </p>
        <p className="footer-credit">
          © {currentYear} | Designed & Built by Mohit and Team Health AI
        </p>
      </div>
    </footer>
  );
}

export default Footer;
