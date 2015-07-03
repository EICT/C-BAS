package admin.cbas.eict.de;

import java.util.HashMap;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.Map;
import java.util.Set;


public class SliceAuthorityAPI {

	static String url = "";
	static String output ="";
	static Object credentials[];
	
	public static void setHostAndPort(String host, int port)
	{
		url = "https://"+host+":"+port+"/sa/2";
	}
	
	@SuppressWarnings("unchecked")
	public static Slice[] lookupSlices(String projectURN)
	{
		Map<String, Object> options = new HashMap<String, Object>();				

		if(projectURN != null)
		{
			Map<String, String> match = new HashMap<String, String>();
			match.put("SLICE_PROJECT_URN", projectURN);
			options.put("match", match);
		}
		
        Object params[] = new Object[]{"SLICE", "", options};
        Map<String, Object> rsp = FAPIClient.execute(url, "lookup", params);
		        
        Integer code = (Integer)rsp.get("code");
        if (code.intValue() != 0)
        {
        	output = (String)rsp.get("output");
        	return null;
        }
        	

        Map<String, Object> x = (Map<String, Object>) rsp.get("value");
        
        Set<String> keyset = x.keySet();
        Slice[] sliceDetails = new Slice[keyset.size()];
        Iterator<String> itr = keyset.iterator();
        int index=0;
        
        while(itr.hasNext())
        {
        	String urn = itr.next();
        	Map<String, String> m = (Map<String, String>)x.get(urn);
        	Slice d = new SliceAuthorityAPI.Slice();
        	d.name = m.get("SLICE_NAME");
        	d.expiry = m.get("SLICE_EXPIRATION");
        	d.uuid = m.get("SLICE_UID");
        	d.urnProject = m.get("SLICE_PROJECT_URN");
        	d.desc = m.get("SLICE_DESCRIPTION");
        	d.creation = m.get("SLICE_CREATION");
        	d.urn = urn;
        	sliceDetails[index++] = d;
        }
        
        return sliceDetails;
	}
	
	
	public static Slice[] lookupAllSlices()
	{
		return lookupSlices(null);
	}
	
	@SuppressWarnings("unchecked")
	public static LinkedList<Membership> lookupMembers(String objURN, String objType)
	{
		Map<String, Object> options = new HashMap<String, Object>();
        Object params[] = new Object[]{objType, objURN, "", options};
		
        Map<String, Object> rsp = FAPIClient.execute(url, "lookup_members", params);
		
        Integer code = (Integer)rsp.get("code");
        if (code.intValue() != 0)
        {
        	output = (String)rsp.get("output");
        	return null;
        }
        
        Object[] values = (Object[]) rsp.get("value");
        LinkedList<Membership> members = new LinkedList<Membership>();
        
        for(int i=0; i<values.length; i++)
        {
        	Map<String, String> m = (Map<String, String>) values[i];
        	String mURN = m.get(objType.toUpperCase()+"_MEMBER");
        	String mRole = m.get(objType.toUpperCase()+"_ROLE");        	
        	members.add(new Membership(mURN, mRole, objType));
        }

        return members;
	}
	
	public static Membership addMember(String objURN, String memberURN, String objType)
	{
		objType = objType.toUpperCase();
		Map<String, String> add_data = new HashMap<String, String>();
		add_data.put(objType+"_MEMBER", memberURN);
		add_data.put(objType+"_ROLE", "MEMBER");		
		
		Map<String, Object> options = new HashMap<String, Object>();
		options.put("members_to_add", new Object[]{add_data});
		
//		Map<String, String> cred = new HashMap<String, String>();
//		cred.put("geni_type", "geni_sfa");
//		cred.put("geni_version", "3");
//		cred.put("geni_value", credStr);		
		
        Object params[] = new Object[]{objType, objURN, credentials, options};
		
        Map<String, Object> rsp = FAPIClient.execute(url, "modify_membership", params);
		
        Integer code = (Integer)rsp.get("code");
        if (code.intValue() != 0)
        {
        	output = (String)rsp.get("output");
        	return null;
        }
        else
        	return new Membership(memberURN, "MEMBER", objType);
        	
	}	

	public static Membership changeMemberRole(String objURN, String memberURN, String newRole, String objType)
	{
		objType = objType.toUpperCase();
		Map<String, String> change_data = new HashMap<String, String>();
		change_data.put(objType+"_MEMBER", memberURN);
		change_data.put(objType+"_ROLE", newRole);	
		
		Map<String, Object> options = new HashMap<String, Object>();
		options.put("members_to_change", new Object[]{change_data});
		
		
        Object params[] = new Object[]{objType, objURN, credentials, options};
		
        Map<String, Object> rsp = FAPIClient.execute(url, "modify_membership", params);
		
        Integer code = (Integer)rsp.get("code");
        if (code.intValue() != 0)
        {
        	output = (String)rsp.get("output");
        	return null;
        }
        else
        	return new Membership(memberURN, newRole, objType);
	}	
	
	public static boolean removeMember(String objURN, String memberURN, String objType)
	{

		objType = objType.toUpperCase();
		Map<String, String> remove_data = new HashMap<String, String>();
		remove_data.put(objType+"_MEMBER", memberURN);
		
		
		Map<String, Object> options = new HashMap<String, Object>();
		options.put("members_to_remove", new Object[]{remove_data});
		
        Object params[] = new Object[]{objType, objURN, credentials, options};
		
        Map<String, Object> rsp = FAPIClient.execute(url, "modify_membership", params);
		
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
	public static Slice addSlice(Slice slice)
	{

		Map<String, String> create_data = new HashMap<String, String>();
		create_data.put("SLICE_NAME", slice.name);
		create_data.put("SLICE_DESCRIPTION", slice.desc);
		create_data.put("SLICE_PROJECT_URN", slice.urnProject);
		
		Map<String, Object> fields = new HashMap<String, Object>();
		fields.put("fields", create_data);
				
        Object params[] = new Object[]{"SLICE", credentials, fields};
		
        Map<String, Object> rsp = FAPIClient.execute(url, "create", params);
		
        Integer code = (Integer)rsp.get("code");
        if (code.intValue() != 0)
        {
        	output = (String)rsp.get("output");
        	return null;
        }
        
        Map<String, String>values = (Map<String, String>) rsp.get("value");
    	slice.expiry = values.get("SLICE_EXPIRATION");
    	slice.uuid = values.get("SLICE_UID");
    	slice.urn = values.get("SLICE_URN");
    	slice.creation = values.get("SLICE_CREATION");

        return slice;
	}	
	
	@SuppressWarnings("unchecked")
	public static Project[] lookupAllProjects()
	{
		Map<String, Object> options = new HashMap<String, Object>();
        Object params[] = new Object[]{"PROJECT", "", options};
		
        Map<String, Object> rsp = FAPIClient.execute(url, "lookup", params);
		
        Integer code = (Integer)rsp.get("code");
        if (code.intValue() != 0)
        {
        	output = (String)rsp.get("output");
        	return null;
        }
        Map<String, Object> x = (Map<String, Object>) rsp.get("value");
        
        Set<String> keyset = x.keySet();
        Project[] projectDetails = new Project[keyset.size()];
        Iterator<String> itr = keyset.iterator();
        int index=0;
        
        while(itr.hasNext())
        {
        	String urn = itr.next();
        	Map<String, String> m = (Map<String, String>)x.get(urn);
        	Project d = new SliceAuthorityAPI.Project();
        	d.name = m.get("PROJECT_NAME");
        	d.expiry = m.get("PROJECT_EXPIRATION");
        	d.uuid = m.get("PROJECT_UID");
        	d.desc = m.get("PROJECT_DESCRIPTION");
        	d.creation = m.get("PROJECT_CREATION");
        	d.urn = urn;
        	projectDetails[index++] = d;
        }
        
        return projectDetails;
	}
	
	@SuppressWarnings("unchecked")
	public static Project addProject(Project project)
	{

		Map<String, String> create_data = new HashMap<String, String>();
		create_data.put("PROJECT_NAME", project.name);
		create_data.put("PROJECT_DESCRIPTION", project.desc);
		
		
		
		Map<String, Object> fields = new HashMap<String, Object>();
		fields.put("fields", create_data);
				
        Object params[] = new Object[]{"PROJECT", credentials, fields};
		
        Map<String, Object> rsp = FAPIClient.execute(url, "create", params);
		
        Integer code = (Integer)rsp.get("code");
        if (code.intValue() != 0)
        {
        	output = (String)rsp.get("output");
        	return null;
        }
        
        Map<String, String>values = (Map<String, String>) rsp.get("value");
        project.expiry = values.get("PROJECT_EXPIRATION");
        project.uuid = values.get("PROJECT_UID");
        project.urn = values.get("PROJECT_URN");
        project.creation = values.get("PROJECT_CREATION");

        return project;
	}	
	
	@SuppressWarnings("unchecked")
	public static LinkedList<AnObject> lookupForMembers(String memberURN, String objType)
	{
		Map<String, Object> options = new HashMap<String, Object>();
		Map<String, Object> filter = new HashMap<String, Object>();
		filter.put(objType+"_URN", new Boolean(true));				
		options.put("filter", filter);
		
        Object params[] = new Object[]{objType, memberURN, "", options};
		
        Map<String, Object> rsp = FAPIClient.execute(url, "lookup_for_member", params);
		
        Integer code = (Integer)rsp.get("code");
        if (code.intValue() != 0)
        {
        	output = (String)rsp.get("output");
        	return null;
        }
        
        Object[] values = (Object[]) rsp.get("value");
        
        LinkedList<AnObject> objects = new LinkedList<AnObject>();
        
        for(int i=0; i<values.length; i++)
        {
        	Map<String, String> m = (Map<String, String>) values[i];        	
        	String urn = m.get(objType.toUpperCase()+"_URN");        	
        	objects.add(new AnObject(urn));
        }

        return objects;
	}

		
	
	//////// inner classes
	
	
	static class Slice implements Comparable<Slice>
	{
		String urn, uuid, name, desc, urnProject, expiry, creation;
		LinkedList<Membership> members;
		
		Slice()
		{
			members = new LinkedList<Membership>();
		}

		@Override
		public int compareTo(Slice arg0) {			
			return name.toLowerCase().compareTo(arg0.name.toLowerCase());
		}
		
		@Override
		public String toString()
		{
			return name;
		}
			
	} //inner-class
	
	static class Membership
	{
		String urn, role, type;
		
		public Membership(String urn, String role, String type)
		{
			this.urn = urn;
			this.role = role;
			this.type = type;
		}
	} //inner-class
	
	static class Project implements Comparable<Project>
	{
		String urn, uuid, name, desc, expiry, creation;
		LinkedList<Membership> members;
		Slice[] slices;
		
		Project()
		{
			members = new LinkedList<Membership>();
		}
			
		@Override
		public int compareTo(Project arg0) {			
			return name.toLowerCase().compareTo(arg0.name.toLowerCase());
		}
		
		@Override
		public String toString()
		{
			return name;
		}
		
	} //inner-class
	
	static class AnObject
	{
		String urn, name;
		AnObject(String name, String urn)
		{
			this.name = name;
			this.urn = urn;
		}
		
		AnObject(String urn)
		{
			this.urn = urn;
			if(urn.indexOf('+') > 0)
				name = urn.substring(urn.lastIndexOf('+')+1);
			else
				name = urn;
		}
		
			
	} //inner-class
	
		
}//class


