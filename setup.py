from distutils.core import setup

setup(name='uuadip',
      version='1.0',
      description='Data Managment Software',
      author='Joe Young',
      author_email='joe.young@utah.edu',
      url='http://www.jsyoung.us/code/',
      packages=['uuadip','uuadip.tools',
		'uuadip.tools.metcalcs',
		'uuadip.formats',
		'uuadip.formats.vaisala',
		'uuadip.formats.ncar',
		'uuadip.formats.ncar.rwp915',
		'uuadip.formats.ncar.nima',
		'uuadip.formats.ncar.nima.rwp915',
		'uuadip.formats.halopho',
		'uuadip.formats.graw',
		'uuadip.formats.general',
		'uuadip.formats.general.lidar',
		'uuadip.formats.general.dem',
		'uuadip.writers',
		'uuadip.writers.rass',
		'uuadip.writers.ncar_vaisala_ceilometer'
		]
     )

