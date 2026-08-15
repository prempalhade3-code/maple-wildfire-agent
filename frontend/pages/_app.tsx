import '../styles/globals.css';
import { GLOBAL_CSS } from '../components/Shared';

function MyApp({ Component, pageProps }: any) {
  return (
    <>
      <style dangerouslySetInnerHTML={{ __html: GLOBAL_CSS }} />
      <Component {...pageProps} />
    </>
  );
}

export default MyApp;
