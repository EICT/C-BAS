package admin.cbas.eict.de;

import java.io.BufferedReader;
import java.security.cert.CertificateException;
import java.security.cert.CertificateFactory;
import java.security.cert.CertificateParsingException;
import java.security.cert.X509CRL;
import java.security.cert.X509Certificate;
import java.text.DateFormat;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Collection;
import java.util.Date;
import java.util.Iterator;
import java.util.List;
import java.util.TimeZone;
import java.io.ByteArrayInputStream;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;

public class Utils {

	static SimpleDateFormat dateFormatter = new SimpleDateFormat("E, MMMM d, yyyy HH:mm:ss, z");
	
	public static String readFile(File file){
		
		String allText=null;
	
		try {			
			FileReader fileReader = new FileReader(file);
			BufferedReader bufferedReader = new BufferedReader(fileReader);
			StringBuffer stringBuffer = new StringBuffer();
			String line;
			while ((line = bufferedReader.readLine()) != null) {
				stringBuffer.append(line);
				stringBuffer.append("\n");
			}
			fileReader.close();
			allText = stringBuffer.toString();
			
		} catch (IOException e) {
			e.printStackTrace();
		}
	
		return allText;
	}
	
	public static X509Certificate decodeCertificate(String certStr)
	{
		CertificateFactory cf=null;
		X509Certificate cert=null; 

		String postfix = "-----END CERTIFICATE-----";
		String cleanCertStr = certStr.substring(0, certStr.indexOf(postfix)+postfix.length());

		try {
			cf = CertificateFactory.getInstance("X.509");
			cert = (X509Certificate) cf.generateCertificate( new ByteArrayInputStream(cleanCertStr.getBytes()));
		} catch (CertificateException e) {
			e.printStackTrace();
		}
		
		return cert;
	}
	
	public static String formatDate(Date d)
	{
		return dateFormatter.format(d);
	}
	
	public static String utcTolocal(String utc)
	{
		DateFormat utcFormat = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'");
		utcFormat.setTimeZone(TimeZone.getTimeZone("UTC"));
		Date date=null;
		if(utc == null)
			return "NULL";
		
		try {
			date = utcFormat.parse(utc);
		} catch (ParseException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		return formatDate(date);
	}
	
	public static X509CRL decodeCRL(String crlStr)
	{
		 X509CRL crl = null;
		 try {		     
		     CertificateFactory cf = CertificateFactory.getInstance("X.509");
		     crl = (X509CRL)cf.generateCRL(new ByteArrayInputStream(crlStr.getBytes()));
		 } catch (Exception e) {
				e.printStackTrace();
		 }
		 
		 return crl;
	}
	
	public static String extractOwnerURN(File certFile)
	{
		String certStr = readFile(certFile);
		X509Certificate cert = decodeCertificate(certStr);
		Collection<List<?>> altNames=null;
		try {
			altNames = cert.getSubjectAlternativeNames();
		} catch (CertificateParsingException e) {
			e.printStackTrace();
		}
		
		if(altNames == null)
			return null;
		
		Iterator<List<?>> itAltNames  = altNames.iterator();
		while(itAltNames.hasNext()){
			 List<?> extensionEntry = (List<?>)itAltNames.next();
			 Integer nameType = (Integer) extensionEntry.get(0);
			 Object name = extensionEntry.get(1);
			 if(nameType == 6 && ((String)name).startsWith("urn:publicid:IDN"))
				 return (String)name;
		}
		
		return "";
	}
	
	
	
}
