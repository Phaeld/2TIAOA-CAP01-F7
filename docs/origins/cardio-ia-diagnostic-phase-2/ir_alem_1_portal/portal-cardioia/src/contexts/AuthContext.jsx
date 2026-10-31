import { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('fake_jwt'));

  useEffect(() => {
    if (token) {
      localStorage.setItem('fake_jwt', token);
    } else {
      localStorage.removeItem('fake_jwt');
    }
  }, [token]);

  const login = (email, password) => {
    if (email === 'admin@cardio.ia' && password === 'admin') {
      const fakeToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...fake_token';
      setToken(fakeToken);
      return true;
    }
    return false;
  };

  const logout = () => {
    setToken(null);
  };

  return (
    <AuthContext.Provider value={{ token, isAuthenticated: !!token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
