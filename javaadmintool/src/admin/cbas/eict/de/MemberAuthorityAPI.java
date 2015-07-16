package admin.cbas.eict.de;

import java.security.cert.X509CRL;
import java.security.cert.X509Certificate;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.Set;

public class MemberAuthorityAPI {
	
	static String url;// = "https://127.0.0.1:8008/ma/2";
	static X509CRL crl;
	static String output = "";
	static Object credentials[];
	
	public static void setHostAndPort(String host, int port)
	{
		url = "https://"+host+":"+port+"/ma/2";
	}

	
	@SuppressWarnings("unchecked")
	public static Member[] lookupAll()
	{
		Map<String, Object> options = new HashMap<String, Object>();
        Object params[] = new Object[]{"MEMBER", "", options};
		String[] filter = {"MEMBER_CERTIFICATE", "MEMBER_EMAIL", "MEMBER_FIRSTNAME", "MEMBER_LASTNAME", "MEMBER_UID", "MEMBER_URN", "MEMBER_USERNAME", "MEMBER_CREDENTIALS"};
		options.put("filter", filter);
                
		
        Map<String, Object> rsp = FAPIClient.execute(url, "lookup", params);
		
        Integer code = (Integer)rsp.get("code");
        if (code.intValue() != 0)
        {
        	output = (String)rsp.get("output");
        	return null;
        }
        Map<String, Object> x = (Map<String, Object>) rsp.get("value");
        
        Set<String> keyset = x.keySet();
        Member[] memDetails = new Member[keyset.size()];
        Iterator<String> itr = keyset.iterator();
        int index=0;
        
        while(itr.hasNext())
        {
        	String urn = itr.next();
        	Map<String, String> m = (Map<String, String>)x.get(urn);
        	Member d = new MemberAuthorityAPI.Member();
        	d.cert = Utils.decodeCertificate(m.get("MEMBER_CERTIFICATE"));
        	d.certStr = m.get("MEMBER_CERTIFICATE");
        	d.email = m.get("MEMBER_EMAIL");
        	d.fName = m.get("MEMBER_FIRSTNAME");
        	d.lName = m.get("MEMBER_LASTNAME");
        	d.urn = urn;
        	d.uuid = m.get("MEMBER_UID");
        	d.username = m.get("MEMBER_USERNAME");
        	d.privileges = Utils.extractPrivileges(m.get("MEMBER_CREDENTIALS"));
        	memDetails[index++] = d;
        }
        
        return memDetails;
	}

	
	@SuppressWarnings("unchecked")
	public static Member lookupMember(String urn)
	{
		
		Map<String, Object> options = new HashMap<String, Object>();
		Map<String, String> match = new HashMap<String, String>();
		match.put("MEMBER_URN", urn);
		options.put("match", match);
		
        Object params[] = new Object[]{"MEMBER", "", options};
        Map<String, Object> rsp = FAPIClient.execute(url, "lookup", params);
        Integer code = (Integer)rsp.get("code");
        if (code.intValue() != 0)
        {
        	output = (String)rsp.get("output");
        	return null;
        }
        Map<String, Object> x = (Map<String, Object>) rsp.get("value");
        Map<String, String> m = (Map<String, String>)x.get(urn);
        
        Member d = new MemberAuthorityAPI.Member();
        d.cert = Utils.decodeCertificate(m.get("MEMBER_CERTIFICATE"));
        d.certStr = m.get("MEMBER_CERTIFICATE");
    	d.email = m.get("MEMBER_EMAIL");
    	d.fName = m.get("MEMBER_FIRSTNAME");
    	d.lName = m.get("MEMBER_LASTNAME");
    	d.urn = urn;
    	d.uuid = m.get("MEMBER_UID");
    	d.username = m.get("MEMBER_USERNAME");
    	d.privileges = Utils.extractPrivileges(m.get("MEMBER_CREDENTIALS"));
        
        return d;
	}
	
	@SuppressWarnings("unchecked")
	public static Member addMember(Member memDetails)
	{
		
		Map<String, String> fields = new HashMap<String, String>();
		fields.put("MEMBER_FIRSTNAME", memDetails.fName);
		fields.put("MEMBER_LASTNAME", memDetails.lName);
		fields.put("MEMBER_USERNAME", memDetails.username);
		fields.put("MEMBER_EMAIL", memDetails.email);
		
		Map<String, Object> options = new HashMap<String, Object>();
		options.put("fields", fields);

		if(memDetails.privileges.size()>0)
			options.put("privileges", memDetails.privileges.toArray());
						
        Object params[] = new Object[]{"MEMBER", credentials, options};
        
        Map<String, Object> rsp = FAPIClient.execute(url, "create", params);
        Integer code = (Integer)rsp.get("code");
        if (code.intValue() != 0)
        {
        	output = (String)rsp.get("output");
        	return null;
        }
        
        Map<String, String> m = (Map<String, String>) rsp.get("value");        
        Member d = new MemberAuthorityAPI.Member();
        d.cert = Utils.decodeCertificate(m.get("MEMBER_CERTIFICATE"));
        d.certStr = m.get("MEMBER_CERTIFICATE");
        d.privateKey = m.get("MEMBER_CERTIFICATE_KEY");
    	d.email = m.get("MEMBER_EMAIL");
    	d.fName = m.get("MEMBER_FIRSTNAME");
    	d.lName = m.get("MEMBER_LASTNAME");
    	d.urn = m.get("MEMBER_URN");;
    	d.uuid = m.get("MEMBER_UID");
    	d.username = m.get("MEMBER_USERNAME");
    	d.privileges = Utils.extractPrivileges(m.get("MEMBER_CREDENTIALS"));
        return d;
	}

	public static boolean updateMemberInfo(Member memDetails)
	{
		
		Map<String, String> fields = new HashMap<String, String>();
		fields.put("MEMBER_FIRSTNAME", memDetails.fName);
		fields.put("MEMBER_LASTNAME", memDetails.lName);
		fields.put("MEMBER_EMAIL", memDetails.email);
		
		
		Map<String, Object> options = new HashMap<String, Object>();
		options.put("fields", fields);
		
        Object params[] = new Object[]{"MEMBER", memDetails.urn, credentials, options};
        Map<String, Object> rsp = FAPIClient.execute(url, "update", params);
        Integer code = (Integer)rsp.get("code");
        if (code.intValue() != 0)
        {
        	output = (String)rsp.get("output");
        	return false;
        }
        else
        	return true;
	}
	
	@SuppressWarnings("unchecked")
	public static Member extendMembership(Member memDetails)
	{
		
		Map<String, String> fields = new HashMap<String, String>();
		fields.put("MEMBER_CERTIFICATE", memDetails.certStr);		
		
		Map<String, Object> options = new HashMap<String, Object>();
		options.put("fields", fields);
		
        Object params[] = new Object[]{"MEMBER", memDetails.urn, credentials, options};
        Map<String, Object> rsp = FAPIClient.execute(url, "update", params);
        Integer code = (Integer)rsp.get("code");
        if (code.intValue() != 0)
        {
        	output = (String)rsp.get("output");
        	return null;
        }

        Map<String, String> m = (Map<String, String>) rsp.get("value");        
        Member d = new MemberAuthorityAPI.Member();
        d.cert = Utils.decodeCertificate(m.get("MEMBER_CERTIFICATE"));
        d.certStr = m.get("MEMBER_CERTIFICATE");
        d.privateKey = m.get("MEMBER_CERTIFICATE_KEY");

        return d;
	}
	
	
	public static boolean fetchCRL()
	{
						
        Object params[] = new Object[]{""};        
        Map<String, Object> rsp = FAPIClient.execute(url, "get_crl", params);
        Integer code = (Integer)rsp.get("code");
        if (code.intValue() != 0)
        {
        	output = (String)rsp.get("output");
        	return false;
        }
        else
        {
        	crl = Utils.decodeCRL((String)rsp.get("value"));
        	return crl != null;
        }
        
	}
	
	public static boolean reovkeMembership(Member memDetails)
	{
		
        Object params[] = new Object[]{memDetails.urn, credentials};        
        Map<String, Object> rsp = FAPIClient.execute(url, "revoke", params);
        Integer code = (Integer)rsp.get("code");
        if (code.intValue() != 0)
        {
        	output = (String)rsp.get("output");
        	return false;
        }
        else
        	return fetchCRL();
        
	}
	
	public static boolean getVersion()
	{
		Map<String, Object> rsp = FAPIClient.execute(url, "get_version", new Object[]{});
        Integer code = (Integer)rsp.get("code");
        if (code.intValue() != 0)
        {
        	output = (String)rsp.get("output");
        	return false;
        }
        else
        	return true;
	}
	

	public static Object[] getCredential(String memberURN)
	{
		Map<String, Object> options = new HashMap<String, Object>();
				
        Object params[] = new Object[]{memberURN, "", options};
		
		Map<String, Object> rsp = FAPIClient.execute(url, "get_credentials", params);
        Integer code = (Integer)rsp.get("code");
        if (code.intValue() != 0)
        {
        	output = (String)rsp.get("output");
        	return null;
        }

        return (Object[]) rsp.get("value");

	}
	
	public static Object assignPrivileges(String memberURN, Object[] privileges)
	{
        Object params[] = new Object[]{memberURN, credentials, privileges};
		
		Map<String, Object> rsp = FAPIClient.execute(url, "assign_privileges", params);
        Integer code = (Integer)rsp.get("code");
        if (code.intValue() != 0)
        {
        	output = (String)rsp.get("output");
        	return null;
        }

        return rsp.get("value");

	}
	
	static class Member implements Comparable<Member>
	{
		String fName, lName, username, email, urn, uuid, certStr, privateKey;
		X509Certificate cert;
		ArrayList<String> privileges;

		Member()
		{
			privileges = new ArrayList<String>();
		}
		@Override
		public int compareTo(Member o2) {
			return this.username.toLowerCase().compareTo(o2.username.toLowerCase());
		}
		
		@Override
		public String toString() {
			return username;
		}
		
	}
	
	
	
}



