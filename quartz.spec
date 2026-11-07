Name:		quartz
Epoch:		0
Version:	2.3.2
Release:	1
Summary:	Enterprise job scheduler for Java
Group:		Development/Java
License:	ASL 2.0
URL:		https://www.quartz-scheduler.org/
Source0:	https://github.com/quartz-scheduler/quartz/archive/refs/tags/v%{version}.tar.gz#/quartz-%{version}.tar.gz

BuildArch:	noarch
BuildRequires:	python
# Literal, so the first rpmbuild -bs records them before sysjar is installed.
BuildRequires:	maven
BuildRequires:	java-current-devel
BuildRequires:	mvn(org.slf4j:slf4j-api)
# slf4j-api parents this, and a parent POM is not a Requires of the jar.
BuildRequires:	mvn(org.slf4j:slf4j-parent:pom::)
BuildRequires:	mvn(javax.servlet:javax.servlet-api)
# The servlet POM parents jvnet-parent 3, which is rewritten to the published parent.
BuildRequires:	mvn(net.java:jvnet-parent:pom::)
BuildRequires:	mvn(org.jboss.spec.javax.transaction:jboss-transaction-api_1.2_spec)
BuildRequires:	mvn(org.jboss:jboss-parent:pom::)
BuildSystem:	maven
BuildOption(install):	--file-name quartz

Obsoletes:	%{name}-javadoc < %{version}-%{release}

%description
Quartz schedules jobs inside a Java application. 2.3.2 is the last
release before the Jakarta namespace change. This build compiles the
core scheduler against the system SLF4J, Servlet, and JTA jars, and
raises the compiler source level from 1.7 to 1.8. XML schedule dates
are parsed with the JDK datatype factory. c3p0 and HikariCP connection
pools, the jobs module, and the container plugins are left out because
those libraries are not published. Tests are skipped.

%prep
%autosetup -n quartz-%{version}
rm -rf quartz-core/src/test .mvn
python - <<'PY'
import shutil
from pathlib import Path

for path in Path(".").rglob("*.jar"):
    path.unlink()
for path in list(Path(".").rglob("pom.xml")):
    path.unlink()

src = Path("quartz-core/src/main/java")
for rel in (
    "org/quartz/utils/C3p0PoolingConnectionProvider.java",
    "org/quartz/utils/HikariCpPoolingConnectionProvider.java",
):
    path = src / rel
    if not path.is_file():
        raise SystemExit("missing " + rel)
    path.unlink()

factory = src / "org/quartz/impl/StdSchedulerFactory.java"
text = factory.read_text(encoding="utf-8")
old_import = "import org.quartz.utils.C3p0PoolingConnectionProvider;\n"
if old_import not in text:
    raise SystemExit("missing c3p0 import")
text = text.replace(old_import, "", 1)
lines = text.splitlines(keepends=True)
start = next(i for i, line in enumerate(lines) if "instanceof C3p0PoolingConnectionProvider" in line)
end = start + 1
while lines[end].strip() != "}":
    end += 1
del lines[start:end + 1]
text = "".join(lines)
if "instanceof C3p0PoolingConnectionProvider" in text:
    raise SystemExit("c3p0 instanceof remains")
factory.write_text(text, encoding="utf-8")

cubrid = src / "org/quartz/impl/jdbcjobstore/CUBRIDDelegate.java"
text = cubrid.read_text(encoding="utf-8")
text = text.replace("import com.mchange.v2.c3p0.C3P0ProxyConnection;\n", "")
text = text.replace("import java.lang.reflect.Method;\n", "")
lines = text.splitlines(keepends=True)
start = next(i for i, line in enumerate(lines) if "quartz 2.x uses c3p0" in line)
else_at = next(i for i in range(start, len(lines)) if lines[i].strip() == "} else {")
body = []
i = else_at + 1
while lines[i].strip() != "}":
    body.append(lines[i])
    i += 1
end = i + 1
text = "".join(lines[:start] + body + lines[end:])
if "com.mchange" in text or "C3P0ProxyConnection" in text:
    raise SystemExit("c3p0 remains in CUBRIDDelegate")
cubrid.write_text(text, encoding="utf-8")

xml = src / "org/quartz/xml/XMLSchedulingDataProcessor.java"
text = xml.read_text(encoding="utf-8")
old_import = "import javax.xml.bind.DatatypeConverter;\n"
if old_import not in text:
    raise SystemExit("missing DatatypeConverter import")
text = text.replace(
    old_import,
    "import javax.xml.datatype.DatatypeConfigurationException;\n"
    "import javax.xml.datatype.DatatypeFactory;\n",
    1,
)
text = text.replace(
    "DatatypeConverter.parseDateTime(startTimeString).getTime()",
    "xmlDate(startTimeString)",
)
text = text.replace(
    "DatatypeConverter.parseDateTime(endTimeString).getTime()",
    "xmlDate(endTimeString)",
)
anchor = "    protected String getTrimmedToNullString("
helper = """    private static Date xmlDate(String text) throws SAXException {
        try {
            return DatatypeFactory.newInstance().newXMLGregorianCalendar(text).toGregorianCalendar().getTime();
        } catch (DatatypeConfigurationException ex) {
            throw new SAXException(ex);
        }
    }

"""
if anchor not in text:
    raise SystemExit("missing xml anchor")
text = text.replace(anchor, helper + anchor, 1)
if "import javax.xml.bind" in text or "DatatypeConverter.parseDateTime(startTimeString)" in text or "DatatypeConverter.parseDateTime(endTimeString)" in text:
    raise SystemExit("jaxb parse remains")
old_prefixes = "public Iterator<?> getPrefixes(String namespaceURI)"
if old_prefixes not in text:
    raise SystemExit("missing getPrefixes")
# JDK 27's NamespaceContext returns Iterator<String>. Iterator<?> does not override it.
text = text.replace(old_prefixes, "public Iterator<String> getPrefixes(String namespaceURI)", 1)
xml.write_text(text, encoding="utf-8")

java_files = list(src.rglob("*.java"))
if len(java_files) != 202:
    raise SystemExit("java files " + str(len(java_files)))
if list(Path(".").rglob("*.jar")):
    raise SystemExit("prebuilt jar remains")
for path in java_files:
    body = path.read_text(encoding="utf-8")
    for needle in ("com.mchange", "com.zaxxer", "javax.xml.bind"):
        if needle in body:
            raise SystemExit(needle + " remains in " + str(path))

Path("quartz-core/src/main/resources/org/quartz/core/quartz-build.properties").write_text(
    "fullname=Quartz\nname=quartz\nversion=%{version}\n",
    encoding="utf-8",
)

Path("pom.xml").write_text("""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.quartz-scheduler</groupId>
  <artifactId>quartz</artifactId>
  <version>%{version}</version>
  <packaging>jar</packaging>
  <name>Quartz</name>
  <description>Job scheduler. Pool providers that need unpublished libraries are omitted.</description>
  <url>https://www.quartz-scheduler.org/</url>
  <licenses>
    <license>
      <name>Apache License, Version 2.0</name>
      <url>https://www.apache.org/licenses/LICENSE-2.0.txt</url>
    </license>
  </licenses>
  <dependencies>
    <dependency>
      <groupId>org.slf4j</groupId>
      <artifactId>slf4j-api</artifactId>
      <version>1.7.36</version>
    </dependency>
    <dependency>
      <groupId>javax.servlet</groupId>
      <artifactId>javax.servlet-api</artifactId>
      <version>4.0.1</version>
    </dependency>
    <dependency>
      <groupId>org.jboss.spec.javax.transaction</groupId>
      <artifactId>jboss-transaction-api_1.2_spec</artifactId>
      <version>1.1.1.Final</version>
    </dependency>
  </dependencies>
  <properties>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    <maven.compiler.release>8</maven.compiler.release>
  </properties>
  <build>
    <sourceDirectory>quartz-core/src/main/java</sourceDirectory>
    <resources>
      <resource>
        <directory>quartz-core/src/main/resources</directory>
      </resource>
    </resources>
    <plugins>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-compiler-plugin</artifactId>
        <version>3.12.1</version>
        <configuration>
          <release>8</release>
        </configuration>
      </plugin>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-jar-plugin</artifactId>
        <version>3.3.0</version>
      </plugin>
    </plugins>
  </build>
</project>
""", encoding="utf-8")
pom = Path("pom.xml").read_text(encoding="utf-8")
for needle in (
    "<artifactId>quartz</artifactId>",
    "<artifactId>slf4j-api</artifactId>",
    "<version>1.7.36</version>",
    "<artifactId>javax.servlet-api</artifactId>",
    "<artifactId>jboss-transaction-api_1.2_spec</artifactId>",
    "<version>%{version}</version>",
    "<release>8</release>",
    "quartz-core/src/main/java",
):
    if needle not in pom:
        raise SystemExit("pom missing " + needle)
for needle in ("c3p0", "Hikari", "junit", "terracotta", "SNAPSHOT", "<source>", "<target>", "javaee", "javax.xml.bind"):
    if needle in pom:
        raise SystemExit("pom still contains " + needle)
if list(Path(".").rglob("pom.xml")) != [Path("pom.xml")]:
    raise SystemExit("extra pom remains")
PY

%build -a
java --module-path target/quartz-%{version}.jar --describe-module quartz > module-describe.txt
# A versioned jar prints "name@version ... automatic", not "name automatic".
grep -q '^quartz' module-describe.txt || { cat module-describe.txt; exit 1; }
grep -q ' automatic$' module-describe.txt || { cat module-describe.txt; exit 1; }

%files -f .mfiles
%doc readme.adoc docs/license.adoc
