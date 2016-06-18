Nucleator Apache
==================

Nucleator Apache is a Nucleator stackset that provisions and configures a new singleton Apache instance in the specified Nucleator Cage.

The apache instance is not autoscaling.  The stackset is intended as a template for development and deployment of ad-hoc instances within Nucleator Cages that you would like to mantain using infrastructure-as-code.

To see the full list of supported options, use the command:

> nucleator apache --help