%{?_javapackages_macros:%_javapackages_macros}
Summary:        Enterprise Job Scheduler for Java
Name:           quartz
Version:        2.1.7
Release:        9.0%{?dist}
Epoch:          0
License:        ASL 2.0
URL:            http://www.quartz-scheduler.org/
# svn export http://svn.terracotta.org/svn/quartz/tags/quartz-2.1.7
# tar caf quartz-2.1.7.tar.xz quartz-2.1.7
Source0:        %{name}-%{version}.tar.xz

BuildRequires:  java-devel >= 0:1.5.0

BuildRequires:  maven-local
BuildRequires:  maven-checkstyle-plugin
BuildRequires:  maven-clean-plugin
BuildRequires:  maven-dependency-plugin
BuildRequires:  maven-enforcer-plugin
BuildRequires:  maven-pmd-plugin
BuildRequires:  maven-release-plugin
BuildRequires:  maven-shared
BuildRequires:  maven-source-plugin
BuildRequires:  rmic-maven-plugin

BuildRequires:  mvn(com.mchange:c3p0)
BuildRequires:  mvn(org.apache.geronimo.specs:specs)
BuildRequires:  mvn(org.apache.geronimo.specs:geronimo-commonj_1.1_spec)
BuildRequires:  mvn(org.apache.geronimo.specs:geronimo-ejb_2.1_spec)
BuildRequires:  mvn(javax.jms:jms)
BuildRequires:  mvn(javax.mail:mail) >= 1.4.3
BuildRequires:  mvn(javax.servlet:servlet-api) >= 2.5
BuildRequires:  mvn(javax.transaction:jta)
BuildRequires:  mvn(javax.xml.bind:jaxb-api)
BuildRequires:  mvn(log4j:log4j)
BuildRequires:  mvn(org.slf4j:slf4j-api)
BuildRequires:  mvn(org.slf4j:slf4j-log4j12)

# test deps
BuildRequires:  mvn(asm:asm)
BuildRequires:  mvn(junit:junit)
BuildRequires:  mvn(org.apache.derby:derby)
BuildRequires:  mvn(org.hamcrest:hamcrest-library) >= 1.2

BuildArch:      noarch

%description
Quartz is a job scheduling system that can be integrated with, or used 
along side virtually any J2EE or J2SE application. Quartz can be used 
to create simple or complex schedules for executing tens, hundreds, or 
even tens-of-thousands of jobs; jobs whose tasks are defined as standard 
Java components or EJBs. 

%package javadoc
Summary:        API docs for %{name}

%description javadoc
This package contains the API Documentation for %{name}.

%prep
%setup -q 
%pom_disable_module quartz-jboss
# Bundles everything
%pom_disable_module quartz-all
%pom_remove_plugin org.codehaus.mojo:findbugs-maven-plugin
# Fix c3p0 groupId
sed -i -e 's/groupId>c3p0</groupId>com.mchange</' quartz/pom.xml
# Fix jms artifactId
sed -i -e 's/artifactId>jms-api</artifactId>jms</' quartz/pom.xml
# Fix junit artifactId
sed -i -e 's/artifactId>junit-dep</artifactId>junit</' quartz/pom.xml

%build

%mvn_file :%{name} %{name}/%{name} %{name} 
%mvn_file :%{name}-backward-compat %{name}/%{name}-backward-compat %{name}-backward-compat
# skip tests for now due to requirement on hamcrest 1.2
%mvn_build -f -- -Dproject.build.sourceEncoding=UTF-8

%install
%mvn_install

%files -f .mfiles
%doc README.txt NOTICE.txt LICENSE.txt

%files javadoc -f .mfiles-javadoc
%doc LICENSE.txt NOTICE.txt

%changelog
* Sun Aug 18 2013 gil cattaneo <puntogil@libero.it> 0:2.1.7-9
- built with XMvn
- fix BR list
- adapt to current guideline
- add links in /usr/share/java/

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:2.1.7-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Mon Jun 10 2013 Orion Poplawski <orion@cora.nwra.com> - 0:2.1.7-1
- Update to 2.1.7
- Use pom macros/sed instead of patch

* Fri Feb 22 2013 Andy Grimm <agrimm@gmail.com> - 0:2.1.2-7
- Add several BuildRequires (RHBZ#914424)

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:2.1.2-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Feb 06 2013 Java SIG <java-devel@lists.fedoraproject.org> - 0:2.1.2-5
- Update for https://fedoraproject.org/wiki/Fedora_19_Maven_Rebuild
- Replace maven BuildRequires with maven-local

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:2.1.2-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Mon Jan 23 2012 Andy Grimm <agrimm@gmail.com> - 0:2.1.2-3
- Make javamail BuildRequires more specific, since classxpathx-mail doesn't have a pom.

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:2.1.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Wed Dec 14 2011 Andy Grimm <agrimm@gmail.com> - 0:2.1.2-1
- Initial Quartz 2.1.x build

