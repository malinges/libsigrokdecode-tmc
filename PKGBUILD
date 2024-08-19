_gitname="libsigrokdecode-tmc"
pkgname=${_gitname}-git
pkgver=r6.dbeda6c
pkgrel=1
pkgdesc="Protocol decoder for Titan Micro Electronics LED driver chips and for logic analyzing application sigrok"
arch=('any')
url="https://github.com/malinges/${_gitname}"
license=('unknown')
groups=()
depends=('libsigrokdecode')
makedepends=('git')
provides=("${pkgname%-git}")
conflicts=("${pkgname%-git}")
replaces=()
backup=()
options=()
install=
source=("git+https://github.com/malinges/${_gitname}.git")
noextract=()
md5sums=('SKIP')

pkgver() {
	cd "$srcdir/${_gitname}"
	printf "r%s.%s" "$(git rev-list --count HEAD)" "$(git rev-parse --short HEAD)"
}

package() {
	cd "$srcdir/${_gitname}"
	install -d "$pkgdir/usr/share/libsigrokdecode/decoders/${_gitname#libsigrokdecode-}"
	install -m644 *.py "$pkgdir/usr/share/libsigrokdecode/decoders/${_gitname#libsigrokdecode-}"
}
