# Maintainer: Your Name <your.email@example.com>

pkgname=aldo
pkgver=1.0.0
pkgrel=1
pkgdesc="Work Hours Tracker and Invoice Generator for Freelancers"
arch=('any')
url="https://github.com/yourusername/aldo"
license=('MIT')
depends=('python' 'python-click' 'python-reportlab' 'python-appdirs')
makedepends=('python-build' 'python-installer' 'python-wheel' 'python-setuptools')
source=("$pkgname-$pkgver.tar.gz")
sha256sums=('SKIP')  # Replace with actual hash when distributing

prepare() {
  cd "$pkgname-$pkgver"
}

build() {
  cd "$pkgname-$pkgver"
  python -m build --wheel --no-isolation
}

package() {
  cd "$pkgname-$pkgver"
  python -m installer --destdir="$pkgdir" dist/*.whl
  
  # Install license
  install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
  
  # Install documentation
  install -Dm644 README.md "$pkgdir/usr/share/doc/$pkgname/README.md"
}