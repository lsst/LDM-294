####################################################
LDM-294: Data Management Organization and Management
####################################################

This document defines the mission, goals and objectives, organization and responsibilities of the LSST Data Management Organization (DMO).
The document is currently scoped to define these elements for the LSST Design and Development, Construction, and Commissioning phases.
It does not presently address any ongoing mission for the DMO during LSST operations.

Links
=====

- Accepted version: https://ls.st/LDM-294
- Drafts: https://ldm-294.lsst.io/v

Building the PDF locally
========================

The document is built using LaTeX, and relies upon the `lsst-texmf <https://lsst-texmf.lsst.io/>`_ and `images <https://github.com/lsst-dm/images>`_ repositories.
It includes the necessary versions of these as git submodules.
To build from scratch::

  git clone https://github.com/lsst/ldm-294
  cd ldm-294
  git submodule init
  git submodule update
  pip install -r requirements.txt
  make



Other notes
===========

The file DM Product Properties.csv is a direct export from Magic Draw and the script makeProductList.py
uses this to update the ProductTree.pdf, productlist.tex and wbslist.tex .

The OSS2DMS and DMS2OSS files are produced by a macro in https://github.com/lsst/LSE-61/tree/master/support
run it through the mkmatrix.py to generate the two tex files. (Tim Jenness)
