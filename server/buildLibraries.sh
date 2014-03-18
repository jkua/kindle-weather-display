#!/bin/sh

# This script builds rsvg-convert and pngcrush, along with their dependencies
# By default, this will install to your home directory. Redefine 
# INSTALL_LOCATION to change this. The code will be built in 
# BUILD_LOCATION/build
# These packages versions are current as of March 17, 2014. 

INSTALL_LOCATION=$HOME
BUILD_LOCATION=$HOME

export PKG_CONFIG_PATH=$INSTALL_LOCATION/lib/pkgconfig
export PATH=$INSTALL_LOCATION/bin:$PATH
export LDFLAGS=-L$INSTALL_LOCATION/lib
export LD_LIBRARY_PATH=$INSTALL_LOCATION/lib
export CPPFLAGS=-I$INSTALL_LOCATION/include

mkdir -p $INSTALL_LOCATION/lib/pkgconfig
mkdir -p $INSTALL_LOCATION/bin
mkdir -p $INSTALL_LOCATION/include

cd $BUILD_LOCATION
mkdir -p build
cd build

wget ftp://sourceware.org/pub/libffi/libffi-3.0.13.tar.gz
tar xavf libffi-3.0.13.tar.gz 
cd libffi-3.0.13
./configure --prefix=$INSTALL_LOCATION
make
make install
cd ..

wget http://ftp.gnome.org/pub/GNOME/sources/glib/2.39/glib-2.39.91.tar.xz
tar xavf glib-2.39.91.tar.xz 
cd glib-2.39.91
./configure --prefix=$INSTALL_LOCATION
make
make install
cd ..

wget http://ftp.gnome.org/pub/GNOME/sources/libcroco/0.6/libcroco-0.6.8.tar.xz
tar xavf libcroco-0.6.8.tar.xz 
cd libcroco-0.6.8
./configure --prefix=$INSTALL_LOCATION
make
make install
cd ..

wget http://ftp.gnome.org/pub/GNOME/sources/gobject-introspection/1.39/gobject-introspection-1.39.90.tar.xz
tar xavf gobject-introspection-1.39.90.tar.xz 
cd gobject-introspection-1.39.90
./configure --prefix=$INSTALL_LOCATION
make
make install
cd ..

wget http://ftp.gnome.org/pub/GNOME/sources/gdk-pixbuf/2.30/gdk-pixbuf-2.30.6.tar.xz
tar xavf gdk-pixbuf-2.30.6.tar.xz 
cd gdk-pixbuf-2.30.6
./configure --prefix=$INSTALL_LOCATION --without-libtiff
make
make install
cd ..

wget http://cairographics.org/releases/pixman-0.32.4.tar.gz
tar xavf pixman-0.32.4.tar.gz 
cd pixman-0.32.4
./configure --prefix=$INSTALL_LOCATION
make
make install
cd ..

wget http://cairographics.org/releases/cairo-1.12.16.tar.xz
cd cairo-1.12.16.tar.xz 
tar xavf cairo-1.12.16.tar.xz 
cd cairo-1.12.16
./configure --prefix=$INSTALL_LOCATION
make
make install
cd ..

wget http://www.freedesktop.org/software/harfbuzz/release/harfbuzz-0.9.26.tar.bz2
tar xavf harfbuzz-0.9.26.tar.bz2 
cd harfbuzz-0.9.26
./configure --prefix=$INSTALL_LOCATION
make
make install
cd ..

wget http://download.savannah.gnu.org/releases/freetype/freetype-2.5.3.tar.bz2
tar xavf freetype-2.5.3.tar.bz2 
cd freetype-2.5.3
./configure --prefix=$INSTALL_LOCATION
make
make install
cd ..

wget http://www.freedesktop.org/software/fontconfig/release/fontconfig-2.11.0.tar.bz2
tar xavf fontconfig-2.11.0.tar.bz2 
cd fontconfig-2.11.0
./configure --prefix=$INSTALL_LOCATION
make
make install
cd ..

wget http://ftp.gnome.org/pub/GNOME/sources/pango/1.36/pango-1.36.2.tar.xz
tar xavf pango-1.36.2.tar.xz 
cd pango-1.36.2
./configure --prefix=$INSTALL_LOCATION
make
make install
cd ..

wget http://ftp.gnome.org/pub/GNOME/sources/librsvg/2.40/librsvg-2.40.1.tar.xz
tar xavf librsvg-2.40.1.tar.xz 
cd librsvg-2.40.1
./configure --prefix=$INSTALL_LOCATION
make
make install
cd ..

wget http://downloads.sourceforge.net/project/pmt/pngcrush/1.7.73/pngcrush-1.7.73.tar.xz
tar xavf pngcrush-1.7.73.tar.xz 
cd pngcrush-1.7.73
./configure --prefix=$INSTALL_LOCATION
make
cp pngcrush ~/bin
