package admin.cbas.eict.de;

import java.io.File;
import java.io.FileInputStream;
import java.net.URL;
import java.security.KeyFactory;
import java.security.KeyStore;
import java.security.PrivateKey;
import java.security.SecureRandom;
import java.security.cert.CertificateException;
import java.security.cert.CertificateFactory;
import java.security.cert.X509Certificate;
import java.security.spec.PKCS8EncodedKeySpec;
import java.util.HashMap;
import java.util.Map;
import javax.net.ssl.HostnameVerifier;
import javax.net.ssl.HttpsURLConnection;
import javax.net.ssl.KeyManagerFactory;
import javax.net.ssl.SSLContext;
import javax.net.ssl.TrustManager;
import javax.net.ssl.X509TrustManager;
import org.apache.ws.commons.util.NamespaceContextImpl;
import org.apache.xmlrpc.client.XmlRpcClient;
import org.apache.xmlrpc.client.XmlRpcClientConfigImpl;
import org.apache.xmlrpc.common.TypeFactoryImpl;
import org.apache.xmlrpc.common.XmlRpcController;
import org.apache.xmlrpc.common.XmlRpcStreamConfig;
import org.apache.xmlrpc.parser.NullParser;
import org.apache.xmlrpc.parser.TypeParser;
import org.apache.xmlrpc.serializer.NullSerializer;
import org.apache.xmlrpc.serializer.TypeSerializer;
import org.xml.sax.SAXException;

public class FAPIClient {
		
	static KeyManagerFactory kmf;
	static TrustManager[]  trustManagers;	
	
	
	public static void init(File certificateFile, File privateKeyFile) throws Exception
	{
		String keyText = Utils.readFile(privateKeyFile);
		keyText = keyText.replace("-----BEGIN PRIVATE KEY-----\n", "");
		keyText = keyText.replace("-----END PRIVATE KEY-----", "");
		
		byte [] decoded = org.bouncycastle.util.encoders.Base64.decode(keyText);
		PKCS8EncodedKeySpec keySpec = new PKCS8EncodedKeySpec(decoded);
        KeyFactory kf = KeyFactory.getInstance("RSA");
        PrivateKey privKey = kf.generatePrivate(keySpec);

        CertificateFactory cf = CertificateFactory.getInstance("X.509");
        FileInputStream in = new FileInputStream(certificateFile);
        X509Certificate c = (X509Certificate) cf.generateCertificate(in);
        in.close();
        
        KeyStore ks = KeyStore.getInstance(KeyStore.getDefaultType());
        ks.load(null);
        KeyStore.PrivateKeyEntry pkEntry = new KeyStore.PrivateKeyEntry(privKey, new X509Certificate[]{c});
        KeyStore.ProtectionParameter protParam = new KeyStore.PasswordProtection(new char[]{'a','b','c'});
        ks.setEntry("myCert", pkEntry, protParam);
        kmf = KeyManagerFactory.getInstance(
        		   KeyManagerFactory.getDefaultAlgorithm());
        		kmf.init(ks, new char[]{'a','b','c'});

       // Create empty HostnameVerifier
       HostnameVerifier hostVerifier = new HostnameVerifier() {
                            public boolean verify(String arg0, javax.net.ssl.SSLSession arg1) {
                                    return true;
                            }
                };
       HttpsURLConnection.setDefaultHostnameVerifier(hostVerifier);
       
       //Create trust all manager
       trustManagers =       new TrustManager[]{new X509TrustManager(){
                	public void checkClientTrusted( X509Certificate[] x509Certificates, String authType) throws CertificateException {}
                	public void checkServerTrusted( X509Certificate[] x509Certificates, String authType) throws CertificateException {}
                	public X509Certificate[] getAcceptedIssuers(){	return new X509Certificate[0];}
                	}} ;               
	}
	
	
	@SuppressWarnings("unchecked")
	public static Map<String, Object> execute(String urlString, String method, Object[] params)
	{
		Map<String, Object> rsp=null;
		
		try {
	        SSLContext context = SSLContext.getInstance("SSL");
	        context.init(kmf.getKeyManagers(),trustManagers, new SecureRandom());
	        HttpsURLConnection.setDefaultSSLSocketFactory(context.getSocketFactory());        		

	        XmlRpcClientConfigImpl config = new XmlRpcClientConfigImpl();
	        config.setServerURL(new URL(urlString));
	        XmlRpcClient client = new XmlRpcClient();
	        client.setTypeFactory(new XmlRpcTypeNil(client)); 
	        client.setConfig(config);
			rsp = (Map<String, Object>) client.execute(method, params);
			
		} catch (Exception ex) {
//			StringWriter errors = new StringWriter();
//			ex.printStackTrace(new PrintWriter(errors));
//			String errorMessage = errors.toString();
//			//rsp.put("output", errorMessage);
			ex.printStackTrace();
			String userFriendlyMessage = "";
			if(ex.getMessage().contains("invalid"))
				userFriendlyMessage = "Certificate or key file contents are unexpected.<br/> <br/> ("+ex.getMessage()+")";
			else if (ex.getMessage().contains("decrypt_error"))
				userFriendlyMessage = "Failed to establish secure connection.Probably given key does not correspond to the certificate.<br/> <br/> ("+ex.getMessage()+")";
			else if (ex.getMessage().contains("refused"))
				userFriendlyMessage = "Could not connect to C-BAS host. Check if C-BAS is running and given host/port are correct.<br/> <br/> ("+ex.getMessage()+")";
			else
				userFriendlyMessage = ex.getMessage();
			
			rsp = new HashMap<String, Object>();
			rsp.put("code", new Integer(-1));			
			rsp.put("output", userFriendlyMessage);
			rsp.put("value", "");
		}
        return rsp;
	}
	

}//class

class XmlRpcTypeNil extends TypeFactoryImpl {

	public XmlRpcTypeNil(XmlRpcController pController) {
		super(pController);
	}

	public TypeParser getParser(XmlRpcStreamConfig pConfig, NamespaceContextImpl pContext, String pURI, String pLocalName) {
		if (NullSerializer.NIL_TAG.equals(pLocalName) || NullSerializer.EX_NIL_TAG.equals(pLocalName) )return new NullParser();
		else return super.getParser(pConfig, pContext, pURI, pLocalName);
	}

	public TypeSerializer getSerializer(XmlRpcStreamConfig pConfig, Object pObject) throws SAXException {
		if (pObject instanceof XmlRpcTypeNil) return new NullSerializer();
		else return super.getSerializer(pConfig, pObject);
	}
}
