# Wix to WooCommerce Product Exporter

A Python script to convert product exports from Wix to WooCommerce-compatible CSV format.

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- Converts Wix product CSV exports to WooCommerce import format
- Handles both simple and variable products
- Maintains product variants and inventory
- Converts image references to proper Wix URLs
- Preserves product descriptions and metadata
- Supports multiple product attributes
- Generates proper product categories mapping

## Requirements

- Python 3.7+
- pandas
- BeautifulSoup4

## Installation

1. Clone repository:
```bash
git clone https://github.com/alsahlawi/wix-to-woocommerce.git
cd wix-to-woocommerce-exporter
