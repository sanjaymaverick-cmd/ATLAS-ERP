from setuptools import find_packages, setup

setup(
	name="erpatlas",
	version="0.1.0",
	description="Real-estate ERP on ERPNext",
	author="Atlas",
	author_email="md@atlas.local",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=[],
)
