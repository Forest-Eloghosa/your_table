/* Patch for Bootstrap Carousel: defensive checks to avoid null .classList errors
   This monkey-patches bootstrap.Carousel._setActiveIndicatorElement to skip
   indicator updates when the indicators container or elements are missing.
*/
(function () {
  if (!window.bootstrap || !bootstrap.Carousel || !bootstrap.Carousel.prototype) {
    return;
  }

  var proto = bootstrap.Carousel.prototype;

  if (typeof proto._setActiveIndicatorElement !== 'function') {
    return;
  }

  var original = proto._setActiveIndicatorElement;

  proto._setActiveIndicatorElement = function (index) {
    // If there is no indicators element, nothing to do
    if (!this._indicatorsElement) {
      return;
    }

    // Find currently active indicator and remove active state if present
    try {
      var activeIndicator = this._indicatorsElement.querySelector('.active');
      if (activeIndicator) {
        activeIndicator.classList.remove('active');
        activeIndicator.removeAttribute('aria-current');
      }
    } catch (e) {
      // Defensive: if querySelector or classList fails for any reason, bail out
      return;
    }

    // Find the new indicator and set it active if present
    var newActiveIndicator = this._indicatorsElement.querySelector('[data-bs-slide-to="' + index + '"]');
    if (newActiveIndicator) {
      newActiveIndicator.classList.add('active');
      newActiveIndicator.setAttribute('aria-current', 'true');
    }
  };
})();
