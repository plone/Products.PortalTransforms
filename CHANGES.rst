Changelog
=========

.. You should *NOT* be adding new change log entries to this file.
   You should create a file in the news directory instead.
   For helpful instructions, please see:
   https://github.com/plone/plone.releaser/blob/master/ADD-A-NEWS-ITEM.rst

.. towncrier release notes start

3.1.9 (2020-09-07)
------------------

Bug fixes:


- Fixed deprecation warning for DocumentTemplate.DT_Util.html_quote.
  [maurits] (#41)


3.1.8 (2020-04-23)
------------------

Bug fixes:


- Minor packaging updates. (#1)
- Use markdown extension settings from markup control panel.
  [pabo3000, thomasmassmann] (#30)


3.1.7 (2019-05-21)
------------------

Bug fixes:


- Fix: 'DeprecationWarning: Flags not at the start of the expression'
  [jensens] (#40)


3.1.6 (2019-03-02)
------------------

Bug fixes:


- When form tag is added to the valid tags, do not remove it anyway.
  By default the cleaner would always remove form tags and kill button, input, select, and textarea tags
  Fixes `issue 2693 <https://github.com/plone/Products.CMFPlone/issues/2693>`_.
  [maurits] (#2693)


3.1.5 (2018-11-01)
------------------

Bug fixes:


- Some transform were returning unicode instead of strings in Python 2 (#37)
- fix scrub_html when passing unicode [pbauer] (#38)


3.1.4 (2018-09-23)
------------------

Bug fixes:

- fix test for python 3
  [petschki]


3.1.3 (2018-06-21)
------------------

Bug fixes:

- Start fixing startup in py3
  [ale-rt, pbauer]

- Stop using ATTestCase for tests.
  [davisagli]


3.1.2 (2018-02-05)
------------------

Bug fixes:

- Add Python 2 / 3 compatibility.  [maurits]


3.1.1 (2017-11-24)
------------------

Bug fixes:

- Do not expose dead settings in ``safe_html`` ZMI settings page.
  This fixes `Products.CMFPlone #2130 <https://github.com/plone/Products.CMFPlone/issues/2130>`_
  [jensens]


3.1 (2017-09-03)
----------------

Breaking changes:

- Fix and migrate safe_html filter completly into Plone registry and sync settings with TinyMCE.
  Also some unused options in controlpanel where removed, like stripped_combinations and class_blacklist.
  [MrTango]


3.0.0 (2017-04-02)
------------------

Breaking changes:

- Use lxml.html.Cleaner for safe HTML transforms (PLIP 1441)
  [prakharjoshi, tomgross]


2.2.2 (2017-02-20)
------------------

New features:

- Add the possibility to switch on markdown extension through the zmi.
  [pabo3000]


2.2.1 (2016-08-19)
------------------

Fixes:

- Fix regression in rest transform vs. old Zope2 reStructuredText wrapper:
  headings now proper level in settings for body, which was necessary to
  preserve levels assumed in downstream use of this transform
  (e.g. Archetypes).  Behavior now matches that of previous wrapper.
  [seanupton]


2.2.0 (2016-02-14)
------------------

New:

- Use docutils for rest since the rest-wrapper was removed from zope2.
  [pbauer]

- Depend on ``Pillow>=3.1.0``.
  [jensens]

- Add the fenced_code_blocks extension for Markdown Transformations
  and depend on Markdown >=2.6.5.
  https://pythonhosted.org/Markdown/extensions/fenced_code_blocks.html
  [pcdummy]

Fixes:

- Fix: After using ``Pillow>=3.1.0`` fix TIFF test output for this new
  version of Pillow writing a ``dword`` instead of a ``word`` as type in
  the IFD header for the width.
  [jensens]

- Fix output of TransformTest to not contain binary in case of failure. This
  broke the test result parser.
  [jensens]

- cleanup: autopep8, isort sorted imports, utf8 header, security decorators,
  zca decorators, minor manual edits
  [jensens]

- Make tests compatible with OS other than Ubuntu 14.04.
  [do3cc]


2.1.10 (2015-09-15)
-------------------

- Add iframe as a valid tag
  [vangheem]


2.1.9 (2015-09-04)
------------------

- fix unicode issue in safe_html when there is entity in script tag
  [gotcha]


2.1.8 (2015-08-20)
------------------

- fix error mis-configured transforms would cause:
  "AttributeError: 'NoneType' object has no attribute 'items'"
  [vangheem]


2.1.7 (2015-06-24)
------------------

- fix safe_html with entities after a <script> tag
  [gotcha]

- Remove CMFDefault dependency
  [tomgross]


2.1.6 (2015-04-22)
------------------

- Do not escape <, >, and & inside script tag when it is not suppressed.
  [gotcha]


2.1.5 (2015-03-13)
------------------

- Do not fail tests if a mimetype already has been registered in the tests.
  [timo]

- Update output gif; Pillow 2.7.0 no longer optimizes the palette of gifs in RGB mode.
  [davisagli]


2.1.4 (2014-09-07)
------------------

- Don't force utf-8 when sub is run on a unicode string. This fixes
  unicodedecodeerror when we have a match in a unicode string containing
  non ascii chars.
  [tmog]


2.1.3 (2014-01-27)
------------------

- Nothing changed.


2.1.2 (2012-12-09)
------------------

- Adjust safe_html transform to block various XSS vulnerabilities. This fixes
  https://plone.org/products/plone/security/advisories/20121106/18
  [davisagli]


2.1.1 (2012-10-05)
------------------

- Do not try to handle invalid tags : we take for granted that html coming out
  of converters do not hold any of embed, script, object or applet tags.


2.1 (2012-10-05)
----------------

- Avoid throwing exceptions on js attrs and invalid tags in word_to_html
  transform
  [gotcha]

- Handle charrefs & entityrefs in data and attributes equaly (unchanged)
  if converting to safe_html
  [tom_gross]


2.0.7 - 2011-07-04
------------------

The following three changes collectively fix
http://plone.org/products/plone/security/advisories/CVE-2011-1949

- In the safe_html transform, abort parsing if a broken declaration is found.
  [evilbungle, davisagli]

- In the safe_html transform, remove data URIs.
  [davisagli]

- In the safe_html transform, ignore null bytes when checking for unsafe
  attributes with scripts.
  [davisagli]


2.0.6 - 2011-04-03
------------------

- Update RoleManager import to avoid deprecation warning on Zope 2.13.
  [davisagli]

2.0.5 - 2011-02-26
------------------

- Fix regression due to the security declarations added in 2.0.4: convertTo
  should still be public, but not publishable.
  [davisagli]

2.0.4 - 2011-02-25
------------------

- Fix missing security declarations.
  [davisagli]

2.0.3 - 2010-11-24
------------------

- Fix manage_options which accidentally got turned into a tuple in some
  refactoring.
  [swampmonkey]

- Added missing `url` metadata.
  [hannosch]

2.0.2 - 2010-10-27
------------------

* Close ``<p>`` tags properly in ``configureTransform.zpt``.
  [swampmonkey]

* Add HTML5 tags as valid: `article`, `aside`, `audio`, `canvas`, `command`,
  `datalist`, `details`, `figcaption`, `figure`, `footer`, `header`, `hgroup`,
  `keygen`, `mark`, `rp`, `rt`, `ruby`, `section`, `source`, `summary`,
  `time`, `video`.
  [limi]

2.0.1 - 2010-07-18
------------------

* Use the standard libraries doctest module.
  [hannosch]

* Added `padding-left` to the style whitelist, to let TinyMCE's indent work.
  This closes http://dev.plone.org/plone/ticket/10557.
  [hannosch]

* PEP8 adjustments for the safe_html transform.
  [hannosch]

2.0 - 2010-07-16
----------------

* Lower test requirements for transform tests to only check the start of each
  file. There's too many subtle differences in the exact output on different
  machines.
  [hannosch]

* PEP8 cleanup of the transform engine code.
  [hannosch]

2.0b6 - 2010-06-13
------------------

* Repeat safe_html transform to block a malicious HTML injection vector.
  Thanks to evilbungle for the report.
  [MatthewWilkes]

2.0b5 - 2010-04-10
------------------

* Let mimetype maps with empty transform lists be handled more gracefully.
  Fixes: http://dev.plone.org/plone/ticket/10402, refs: r12421.
  [thet]

* Fixed a problem where the cache would return data from transforms
  which are sensitive to virtual hosting (such as the resolve UID
  transforms used by visual editors) which had been cached for a
  different virtual host.
  [rossp]

2.0b4 - 2010-03-01
------------------

* Restore output/logo.jpg and output/logo.bmp from 1.6 branch.
  [stefan]

2.0b3 - 2010-02-19
------------------

* Make tests pass with poppler's pdftohtml converter. Standalone
  pdftohtml produces different output and should be avoided.
  [stefan]

2.0b2 - 2010-02-05
------------------

* Updated expected output images to most current format.
  [hannosch]

2.0b1 - 2010-01-03
------------------

* Fixed a serious performance issue in the find transform path algorithm.
  This refs http://dev.plone.org/plone/ticket/9497.
  [hannosch, sig]

* Protect against failures in the transform engine, which prevented zexp
  imports of sites.
  [hannosch]

* Fixed package dependency declaration.
  [hannosch]

2.0a2 - 2009-12-02
------------------

* Added HTML5 tags as allowed tags.
  [limi]

* Made sure the meta tag is stripped, since not doing it can let things like
  HTML redirects slip through, which makes for unpredictable behavior.
  [limi]

* Added style to nasty tags, addresses http://dev.plone.org/plone/ticket/9015.
  [jonstahl]

2.0a1 - 2009-11-13
------------------

* Added stripped_attributes, stripped_combinations, style_whitelist and
  class_blacklist attributes to the safe_html transform.
  [robgietema]

* Avoid acquiring `mimetypes_registry` and call it via a proper API.
  [hannosch]

* Downgraded log messages about unavailable binaries to debug level.
  [hannosch]

* Updated test output to be compatible with docutils 0.5.
  [hannosch]

* Removed z3 sub-package. Interfaces are in the interfaces module.
  [hannosch]

* Cleaned up package metadata.
  [hannosch]

* Declare test dependencies in an extra and fixed deprecation warnings
  for use of Globals.
  [hannosch]

* Made the graph tests conditional on the availability of the external
  binaries for the transform.
  [hannosch]

* Removed useless assert statements.
  [hannosch]

* Structured Text is gone in Zope 2.12.
  [hannosch]

* Transforms to target mimetype with multiple alias mimetypes in
  mimetypes_registry failed. This closes
  http://dev.plone.org/plone/ticket/8187.
  [hannosch]

* Added logging to markdown and textile transforms if the libraries are not
  installed. This closes http://dev.plone.org/plone/ticket/8285.
  [hannosch]

* Purge old zope2 Interface interfaces for Zope 2.12 compatibility.
  Consider branching before this checkin if releases required before Plone 4.
  [elro]

1.6.4 - 2009-10-08
------------------

* Clean up temporary files/directories after memory errors and failed
  conversions.
  [witsch]

1.6.3 - 2009-09-09
------------------

* Fix handling of CDATA sections.
  [optilude]

1.6.2 - 2009-06-18
------------------

* Fix NameError in the purgeCache method.
  [davisagli]

* Fix the way that unsafe transforms calls the input file for the command line
  plugin.
  [encolpe]

* Make markdown transformation unicode safe and depend on Markdown>=1.7
  [tomster]

1.6.1 - 2008-09-30
------------------

* Fixed rest tests when run on Zope 2.11. The raw and include directives are
  disabled but no longer removed.
  [hannosch]

* Disabled markdown and textile tests when their libraries aren't installed
  [fschulze]

* Implemented entity conversion in html to plain text transform.
  [fschulze]

* Added metadata.xml file to the profile.
  [hannosch]

* Allowed the abbr, acronym, var, dfn, samp, address, bdo, thead, tfoot,
  col, and colgroup tags by default, since they are harmless, valid XHTML
  and shouldn't be filtered. Fixes:
  http://dev.plone.org/plone/ticket/6712 and
  http://dev.plone.org/plone/ticket/7251
  [limi]

* Added proper Z3 interfaces and added direct implements statements instead
  of applying the changes later on with zcml. Reduced number of zcml files
  to one.
  [hannosch]

1.6.0 - 2007-08-16
------------------

1.6.0-rc2 - 2007-07-27
----------------------

* Updated componentregisty.xml to new style.
  [hannosch]

1.6.0-rc1 - 2007-07-04
----------------------

1.6.0-b4 - 2007-04-28
---------------------

* Go back to using getToolByName for CMF tools.
  [wichert]

1.6.0-b3 - 2007-03-20
---------------------

* Removed tests/runalltests.py and tests/framework.py as they have
  outlived their usefulness. To run tests use Zope's testrunner:
  ./bin/zopectl test --nowarn -s Products.PortalTransforms
  [stefan]

1.6.0-b2 - 2007-03-05
---------------------

* Adjusted rest tests for Zope 2.10 output.
  [hannosch]

1.6.0-b1 - 2007-02-27
---------------------

* XXX Please use HISTORY.txt when you make changes

1.6.0-a1 - 2007-02-06
---------------------

* Implemented PLIP 149
  [tomster]

1.5.2 - Unreleased
------------------

* Add another XSS fix from for handling extraneous brackets.
  [dunny]

* Add XSS fixes from Anton Stonor to safe_html transform.
  [alecm, stonor]

1.5.1-final - 2007-04-17
------------------------

* note for release-managers: The version-bump to 1.5 was a bit early, but now
  as we have it, i keep it and next release number in the cycle needed for
  Archetypes 1.4.2 (used for Plone 2.5.2) of PortalTransforms is then the 1.5
  final.
  We dont need increasing of release numbers because of Plone 3.0,
  Archetypes 1.5, ... if theres no change in the dependen product, like
  this one.
  [jensens]

1.5.0-final - 2006-12-15
------------------------

1.5.0-a1 - 2006-10-25
---------------------

* casting to int is evil without previous check of the type. so we assume as
  in CMFPlone just zero for non-int-castable values.
  [jensens]

* the values in the safe_html valid tag dictionary can become strings when
  modifying them via the ZMI. Explicitly convert them to integers before
  testing their value.
  [wichert]

1.4.1-final - 2006-09-08
------------------------

* Shut down a noisy logging message to DEBUG level.
  [hannosch]

* Converted logging infrastructure from zLOG usage to Python's logging module.
  [hannosch]

* Avoid DeprecationWarning for manageAddDelete.
  [hannosch]

* Spring-cleaning of tests infrastructure.
  [hannosch]

1.4.0-beta1 - 2006-03-26
------------------------

* removed odd archetypes 1.3 style version checking
  [jensens]

* Removed BBB code for CMFCorePermissions import location.
  [hannosch]

* removed deprecation-warning for ToolInit
  [jensens]

1.3.9-final02 - 2006-01-15
--------------------------

* nothing - the odd version checking needs a version change to stick to
  Archetypes version.
  [yenzenz]

1.3.9-RC1 - 2005-12-29
----------------------

* Fixed [ 1293684 ], unregistered Transforms are not unmaped,
  Transformation was deleted from portal_transforms, but remained
  active.
  http://sourceforge.net/tracker/index.php?func-detail&aid-1293684&group_id-75272&atid-543430
  Added a cleanup that unmaps deleted transforms on reinstall
  [csenger]

* Replaced the safe_html transformation with a configurable version
  with the same functionality. Migration is handled on reinstall.
  http://trac.plone.org/plone/ticket/4538
  [csenger] [dreamcatcher]

* Removed CoUnInitialize call. According to Mark Hammond: The
  right thing to do is call that function, although almost noone
  does (including pywin32 itself, which does CoInitialize the main
  thread) and I've never heard of problem caused by this
  omission.
  [sidnei]

* Fix a long outstanding issue with improper COM thread model
  initialization. Initialize COM for multi-threading, ignoring any
  errors when someone else has already initialized differently.
  https://trac.plone.org/plone/ticket/4712
  [sidnei]

* Correct some wrong security settings.
  [hannosch]

* Fixed the requirements look-up from the policy
  (#1358085)


1.3.8-final02 - 2005-10-11
--------------------------

* nothing - the odd version checking needs a version change to stick to
  Archetypes version.
  [yenzenz]

1.3.7-final01 - 2005-08-30
--------------------------

* nothing - the odd version checking needs a version change to stick to
  Archetypes version.
  [yenzenz]

1.3.6-final02 - 2005-08-07
--------------------------

* nothing - the odd version checking needs a version change to stick to
  Archetypes version.
  [yenzenz]

1.3.6-final - 2005-08-01
------------------------

* Added q to the list of valid and safe html tags by limi's request.
  Wrote test for safe_html parsing.
  [hannosch]

* Added ins and del to the list of valid and safe html tags.
  [ 1199917 ] XHTML DEL tag is removed during the safe_html conversion
  [tiran]

1.3.5-final02 - 2005-07-17
--------------------------

* changed version to stick to appropiate Archetypes Version.
  [yenzenz]

1.3.5-final - 2005-07-06
------------------------

* pdf_to_html can show images now. Revert it to command transformer and
  make it work under windows.
  [panjunyong]

* refined command based unsafe transform to make it work with windows.
  [panjunyong]

* Disabled office_uno by default because it doesn't support multithread yet
  [panjunyong]

* Rewrote office_uno to make it work for the recent PyUNO.
  [panjunyong]

1.3.4-final01 - 2005-05-20
--------------------------

* nothing (I hate to write this. But the odd version checking needs it).
  [yenzenz]

1.3.4-rc1 - 2005-03-25
----------------------

* Better error handling for safe html transformation
  [tiran]

1.3.3-final - 2005-03-05
------------------------

* Updated link to rtf converter to http://freshmeat.net/projects/rtfconverter/
  [tiran]

* Small fix for the com office converter. COM could crash if word is
  invisible. Also a pop up might appeare when quitting word.
  [gogo]

* Fixed [ 1053846 ] Charset problem with wvware word_to_html conversion
  [flacoste]

* Fixed python and test pre transforms to use html quote special characters.
  Thx to stain. [ 1091670 ] Python source code does not escape HTML.
  [tiran]

* Fixed [ 1121812 ] fix PortalTransforms unregisterTransformation()
  unregisterTransformation() misses to remove from the zodb the persistance
  wrapper added to the trasformation
  [dan_t]

* Fixed [ 1118739 ] popentransform does not work on windows
  [duncanb]

* Fixed [ 1122175 ] extra indnt sytax error in office_uno.py
  [ryuuguu]

* fixed bug with some transformers' temp filename: it tried to use original
  filename which is encoded in utf8 and may contrain invalid charset for my
  Windows server. Just use filename as: unknown.suffix
  [panjunyong]

* STX header level is set to 2 instead of using zope.conf. Limi forced me to
  change it.
  [tiran]

* fixed bug: word_to_html uses office_com under windows

1.3.2-5 - 2004-10-17
--------------------

* Fixed [ 1041637 ] RichWidget: STX level should be set to 3 instead 1. The
  structured text transform is now using the zope.conf option or has an
  optional level paramenter in the convert method.
  [tiran]

* Added win32api.GetShortPathName to libtransforms/commandtransform
  so binaries found in directories which have spaces in their names
  will work as expected
  [runyaga]

1.3.2-4 - 2004-09-30
--------------------

* nothing changed

1.3.2-3 - 2004-09-25
--------------------

* Fixed more unit tests
  [tiran]

1.3.2-2 - 2004-09-17
--------------------

* Fixed [ 1025066 ] Serious persistency bug
  [dmaurer]

* Fixed some unit tests failurs. Some unit tests did fail because the reST
  and STX output has changed slightly.
  [tiran]

* Don't include the first three lines of the lynx output which are url,
  title and a blank line. This fixed also a unit test because the url
  which was a file in the fs did change every time.
  [tiran]

* Fixed a bug in make_unpersistent. It seemed that this method touched values
  inside the mapping.
  [dreamcatcher]

1.3.2-1 - 2004-09-04
--------------------

* Disabled filters that were introduced in 1.3.1-1. The currently used
  transform path algo is broken took too long to find a path.
  [tiran]

* Cleaned up major parts of PT by removing the python only implementation which
  was broken anyway

* Fixed [ 1019632 ] current svn bundle (rev 2942) broken

1.3.1-1 - 2004-08-16
--------------------

* Introduce the concept of filters (one-hop transforms where the source and
  destination are the same mimetype).
  [dreamcatcher]

* Add a html filter to extract the content of the body tag (so we don't get a
  double <body> when uploading full html files).
  [dreamcatcher]

* Change base class for Transform to SimpleItem which is equivalent to the
  previous base classes and provides a nice __repr__.
  [dreamcatcher]

* Lower log levels.
  [dreamcatcher]

* cache.py: Added purgeCache, fixed has cache test.
  [tiran]

* Fixed non critical typo in error message: Unvalid -> Invalid
  [tiran]

1.3.0-3 - 2004-08-06
--------------------

* Added context to the convert, convertTo and __call__ methods. The context is
  the object on which the transform was called.
  [tiran]

* Added isCacheable flag and setCacheable to idatastream (data.py). Now you can
  disable the caching of the result of a transformation.
  [tiran]

* Added __setstate__ to load new transformations from the file system.
  [tiran]

* Fixed [ 1002014 ] Add policy screen doesn't accept single entry
  [tiran]

1.3.0-2 - 2004-07-29
--------------------

* Added workaround for [ 997998 ] PT breaks ZMI/Find [tiran]
