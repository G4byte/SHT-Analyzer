from setuptools import setup

setup(
    name='SHT_Analyzer',
    version='0.1.0',    
    description="Data visualization for IRIS' Solid Hydrogen Target",
    url='https://github.com/G4byte/SHT-Analyzer',
    author='Gabe Gorbet',
    author_email='ggorbet@triumf.ca',
    license='BSD 2-clause',
    packages=['SHT_Analyzer'],
    install_requires=[
                      'numpy',                     
                      ],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',  
        'Operating System :: POSIX :: Linux',        
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)