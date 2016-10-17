Antibarrel components
=====================

The correction process consists of these steps:

#. Identify lines in images.
#. Fit a 2\ :sup:`nd` degree polynomial to every line.
#. Determine relationship between lines and polynomial coefficients.
#. Estimate position of the center of the aberration.
#. Rotate both images, so that lines are horizontal.
#. Repeat previous steps. Take the center of the aberration as the origin of coordinates.
#. Estimate the aberration parameters in the form of relationship of the quadratic coefficient on line position.
#. Use the estimate to construct data points.
#. Feed the data points to the model, calculate aberration parameters in a more conventional way.
#. Perform the compensation.


Creating labels
---------------

``mk_labels.py`` accepts the **value threshold** and **count threshold**.

The script performs following operations:

#. Thresholds the image given a ratio.
#. The isolated regions that was created by the thresholding are labelled.
   Labels are sorted by the pixel count.
#. Indices of labels range from negative to positive:

   * First go labels that have lower pixel count than the count threshold (ascending order).
   * Label 0 is the background.
   * Then go labels with greater pixel count than the count threshold (descending order).

   This is done like this because we are typically interested only in labels with sufficient pixel count and it is convenient to know that label 1 is th "best".
   
The output of the script is a ``.pickle`` file containing these keys:

* ``labels``: The labelled image.
* ``img``: The original image.

This output file can be inspected with ``inspect_labels.py``.


Fitting polynomials
-------------------

``mk_lines.py`` accepts the output of ``mk_labels.py`` and the **grow radius** and **coordinate center**.
It examines the labels and uses the underlying image to fit the polynomial:

#. The image and ordered labels are taken from the input.
#. All labels with positive indices are sequentially processed.
#. The labelled region is dilated (using the supplied radius) and becomes the mask (essentially list of ``x`` and ``y`` pixel coordinates).
#. If the center is supplied, the coordinates are recalculated.
#. The 2\ :sup:`nd` order polynomial is fit using :func:`numpy.polyfit`.

The output of the script is a ``.pickle`` file containing same keys as the input does plus:

* ``lines``: The list of polyfits.


Analyzing fits
--------------

``mk_deps.py`` accepts the output of ``mk_lines.py`` and given the assumption that there is a linear relationship between a line's vertical position and the quadratic coefficient is linear dependency.
Following steps are taken before the actual linear fit is made:

#. Apparent outliers are purged (see documentation for :func:`preclean_rough`.
#. Probable outliers are purged using :func:`statsmodels.formula.api.ols` function.
#. The rest is using in a robust fit using :func:`scipy.optimize.least_squares`.

The output of the script is a ``.pickle`` file containing same keys as the input does plus:

* ``lines_out``: Fits --- list of tuples ``(quadratic coeff, linear coeff, constant coeff)``, simply from the key ``lines``.
* ``fit_quad``: Fit of quadratic coefficient against constant coeff.
* ``fit_lin``: Fit of linear coefficient against constant coeff.
* ``zero_at``: What is the value of constant coeff when the quadratic coeff is zero.
* ``slope``: What is the value of linear coeff in ``zero_at``.


Estimate the center of aberration
---------------------------------

``mk_center.py`` takes (as of 10/2016 two) outputs of ``mk_deps.sh`` and estimates the center of aberration from them.
The estimation is primitively straightforward, we assume that the center lies on lines that have zero quadratic coefficient.
As we have two fits, we have two lines, and we can calculate their intersection.

This formula is used: 

* ``x``: :math:`c_x = (\mathit{zeros_1} - \mathit{zeros_0}) / (\mathit{slopes_0} - \mathit{slopes_1})`
* ``y``: :math:`c_y = c_x \cdot \mathit{slopes_0} + \mathit{zeros_0}`

A file (typically ``CENTER``) is created that contains those coordinates.
What is important --- those coordinates have to be passed to mentioned scripts as arguments later.


Rotate the images
-----------------

``mk_rot.py`` rotates the original input images over a given angle and center.
Due to specifics of the least-square fitting, it makes sense to re-run previous scripts over the rotated images, the new thing is that the coordinate system is not arbitrary any more.


Redo everything again
---------------------

This time, specify the aberration center and produce the ``deps-<n>.pickle`` files.


Deduce datapoints
-----------------

``mk_datapoints.py`` makes a set of points (in original position and where they are percieved when the aberration kicks in) that can be used to compute the canonical parameters of the aberration.
In this step, we are in posession of the knowledge of the aberration in a form that is more useful to simulating it rather than correcting it.

Therefore, we perform these steps:

#. We calculate the mean of the linear dependence of quadratic coeff against the constant one.
#. The points coordinates are distributed in inverse quadratic density (i.e. they are more dense close to the aberration center) in both coordinates.
#. Imaging of fixed number of supposedly straight lines is simulated.
   Note that the only thing we know is that they should be straight, but they are curved.
   We don't know *where* they should appear (i.e. their vertical shift if they are mostly horizontal).


* ``center``: The center of the abberation.
* ``imgsize``: The shape of the image.
* ``quad_fits``: Quadratic coeffs against constant coeffs.
* ``lin_fits``: Linear coeffs against constant coeffs.
* ``lines``: The list of polyfits (as in previous cases).
* ``points``: Data points (list of arrays).
* ``yvals``: Corresponding (to ``points``) values of the constant coeff.
  Note that this is just a hint with no real significance.


Solve the problem
-----------------

``mk_solution.py`` takes the input of ``mk_datapoints.py`` and outputs the aberration coefficients.

These steps are performed:

#. Norming --- typically, the coeffs of the aberration are normed so that the radius of the largest circle that can fit into the image is equal to one.
#. The data are processed.
   Using `the common model <http://www.imagemagick.org/Usage/distorts/#barrel>`_, the aberration can be described in four coefficients.
