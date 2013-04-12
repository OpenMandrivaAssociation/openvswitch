Name:           openvswitch
Version:        1.9.0
Release:        1
Summary:        Open vSwitch daemon/database/utilities

Group: 		System/Cluster

# Nearly all of openvswitch is ASL 2.0.  The bugtool is LGPLv2+, and the
# lib/sflow*.[ch] files are SISSL
# datapath/ is GPLv2 (although not built into any of the binary packages)
# python/compat is Python (although not built into any of the binary packages)
License:        ASL 2.0 and LGPLv2+ and SISSL
URL:            http://openvswitch.org
Source0:        http://openvswitch.org/releases/%{name}-%{version}.tar.gz
Source1:        openvswitch.service
Source2:        openvswitch.init
Source3:        openvswitch.logrotate
Source4:        ifup-ovs
Source5:        ifdown-ovs
Source6:        ovsdbmonitor.desktop
Source7:        openvswitch-configure-ovskmod-var.patch
Source8:        ovsdbmonitor-move-to-its-own-data-directory.patch
# make the kmod name configurable since Fedora kernel ships openvswitch module
# Source7 is not applied, it's used to generate patch0
Patch0:         openvswitch-configure-ovskmod-var-autoconfd.patch
# mv ovsdbmonitordir. Source8 (accepted upstream) is source for patch1
Patch1:         ovsdbmonitor-move-to-its-own-data-directory-automaked.patch
Patch2:         openvswitch-rhel-initscripts-resync.patch

BuildRequires:  systemd-units openssl openssl-devel
BuildRequires:  python python-twisted-core python-twisted-conch python-zope-interface PyQt4
BuildRequires:  desktop-file-utils
BuildRequires:  groff graphviz

Requires:       openssl iproute2 module-init-tools

Requires(post):  systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units

%description
Open vSwitch provides standard network bridging functions and
support for the OpenFlow protocol for remote per-flow control of
traffic.

%package -n python-openvswitch
Summary:        Open vSwitch python bindings
License:        ASL 2.0
BuildArch:      noarch
Requires:       python

%description -n python-openvswitch
Python bindings for the Open vSwitch database

%package -n ovsdbmonitor
Summary:        Open vSwitch graphical monitoring tool
License:        ASL 2.0
BuildArch:      noarch
Requires:       python-openvswitch = %{version}-%{release}
Requires:       python python-twisted-core python-twisted-conch python-zope-interface PyQt4

%description -n ovsdbmonitor
A GUI tool for monitoring and troubleshooting local or remote Open
vSwitch installations.  It presents GUI tables that graphically represent
an Open vSwitch kernel flow table (similar to "ovs-dpctl dump-flows")
and Open vSwitch database contents (similar to "ovs-vsctl list <table>").

%package test
Summary:        Open vSwitch testing utilities
License:        ASL 2.0
BuildArch:      noarch
Requires:       python-openvswitch = %{version}-%{release}
Requires:       python python-twisted-core python-twisted-web

%description test
Utilities that are useful to diagnose performance and connectivity
issues in Open vSwitch setup.

%prep
%setup -q
#%patch0 -p1 -b .ovskmod
#%patch1 -p1 -b .ovsdbmonitordir
#%patch2 -p1 -b .initscripts


%build
%configure2_5x --enable-ssl --with-pkidir=%{_sharedstatedir}/openvswitch/pki OVSKMOD=openvswitch
%make

%install
%makeinstall_std

install -d -m 0755 %{buildroot}/%{_sysconfdir}/openvswitch

src=rhel/usr_share_openvswitch_scripts_sysconfig.template
dst=%{buildroot}/%{_sysconfdir}/sysconfig/openvswitch
install -p -D -m 0644 $src $dst

install -p -D -m 0644 %{SOURCE1} %{buildroot}/%{_unitdir}/openvswitch.service
install -p -D -m 0755 %{SOURCE2} %{buildroot}/%{_datadir}/openvswitch/scripts/openvswitch.init
install -p -D -m 0644 %{SOURCE3} %{buildroot}/%{_sysconfdir}/logrotate.d/openvswitch

install -d -m 0755 %{buildroot}/%{_sysconfdir}/sysconfig/network-scripts/
install -p -m 0755 %{SOURCE4} %{SOURCE5} %{buildroot}/%{_sysconfdir}/sysconfig/network-scripts/

install -d -m 0755 %{buildroot}//%{_sharedstatedir}/openvswitch

install -d -m 0755 %{buildroot}/%{python_sitelib}
mv %{buildroot}//%{_datadir}/openvswitch/python/* %{buildroot}/%{python_sitelib}
rmdir %{buildroot}//%{_datadir}/openvswitch/python/

# Get rid of stuff we don't want to make RPM happy.
rm -f \
    %{buildroot}/%{_bindir}/ovs-controller \
    %{buildroot}/%{_mandir}/man8/ovs-controller.8 \
    %{buildroot}/%{_sbindir}/ovs-vlan-bug-workaround \
    %{buildroot}/%{_mandir}/man8/ovs-vlan-bug-workaround.8 \
    %{buildroot}/%{_sbindir}/ovs-brcompatd \
    %{buildroot}/%{_mandir}/man8/ovs-brcompatd.8

desktop-file-install --dir=%{buildroot}/%{_datadir}/applications %{SOURCE6}

install -d -m 0755 %{buildroot}/%{_datadir}/ovsdbmonitor

%post
if [ $1 -eq 1 ] ; then
    # Initial installation
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
fi

%preun
if [ "$1" = "0" ]; then
    # Package removal, not upgrade
    /bin/systemctl --no-reload disable openvswitch.service > /dev/null 2>&1 || :
    /bin/systemctl stop openvswitch.service > /dev/null 2>&1 || :
fi

%postun
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -ge 1 ] ; then
    # Package upgrade, not uninstall
    /bin/systemctl try-restart openvswitch.service >/dev/null 2>&1 || :
fi


%files
%{_sysconfdir}/openvswitch/
%config(noreplace) %{_sysconfdir}/logrotate.d/openvswitch
%config(noreplace) %{_sysconfdir}/sysconfig/openvswitch
%{_sysconfdir}/sysconfig/network-scripts/ifup-ovs
%{_sysconfdir}/sysconfig/network-scripts/ifdown-ovs
%{_unitdir}/openvswitch.service
%{_bindir}/ovs-appctl
%{_bindir}/ovs-benchmark
%{_bindir}/ovs-dpctl
%{_bindir}/ovs-ofctl
%{_bindir}/ovs-parse-leaks
%{_bindir}/ovs-pcap
%{_bindir}/ovs-pki
%{_bindir}/ovs-l3ping
%{_bindir}/ovs-parse-backtrace
%{_bindir}/ovs-tcpundump
%{_bindir}/ovs-vsctl
%{_bindir}/ovsdb-client
%{_bindir}/ovsdb-tool
# ovs-bugtool is LGPLv2+
%{_sbindir}/ovs-bugtool
%{_sbindir}/ovs-vswitchd
%{_sbindir}/ovsdb-server
%{_mandir}/man1/ovs-benchmark.1*
%{_mandir}/man1/ovs-pcap.1*
%{_mandir}/man1/ovs-tcpundump.1*
%{_mandir}/man1/ovsdb-client.1*
%{_mandir}/man1/ovsdb-server.1*
%{_mandir}/man1/ovsdb-tool.1*
%{_mandir}/man5/ovs-vswitchd.conf.db.5*
%{_mandir}/man8/ovs-appctl.8*
%{_mandir}/man8/ovs-bugtool.8*
%{_mandir}/man8/ovs-ctl.8*
%{_mandir}/man8/ovs-dpctl.8*
%{_mandir}/man8/ovs-ofctl.8*
%{_mandir}/man8/ovs-parse-leaks.8*
%{_mandir}/man8/ovs-pki.8*
%{_mandir}/man8/ovs-vsctl.8*
%{_mandir}/man8/ovs-vswitchd.8*
%{_mandir}/man8/ovs-l3ping.1*
%{_mandir}/man8/ovs-parse-backtrace.1*
# /usr/share/openvswitch/bugtool-plugins and
# /usr/share/openvswitch/scripts/ovs-bugtool* are LGPLv2+
%{_datadir}/openvswitch/
%{_sharedstatedir}/openvswitch
# see COPYING for full licensing details
%doc COPYING DESIGN INSTALL.SSL NOTICE README WHY-OVS rhel/README.RHEL

%files -n python-openvswitch
%{python_sitelib}/ovs
%doc COPYING

%files -n ovsdbmonitor
%{_bindir}/ovsdbmonitor
%{_mandir}/man1/ovsdbmonitor.1*
%{_datadir}/ovsdbmonitor
%{_datadir}/applications/ovsdbmonitor.desktop
%doc ovsdb/ovsdbmonitor/COPYING

%files test
%{_bindir}/ovs-test
%{_bindir}/ovs-vlan-test
%{_mandir}/man8/ovs-test.8*
%{_mandir}/man8/ovs-vlan-test.8*
%{python_sitelib}/ovstest
