import { NextCookies } from "next/dist/server/web/spec-extension/cookies";

export const APP_COOKIES_AUTH = "SPOTIFY_ROOMS_AUTHENTICATION";

export const APP_COOKIES_ACCESS = "SPOTIFY_ROOMS_ACCESS";

export const getCookieSetOptions = (maxAge = 60 * 60 * 24 * 10) => {
    return {
        httpOnly: true,
        path: "/",
        secure: "development" !== process.env.NODE_ENV,
        maxAge,
    };
};

export const COOKIES_DEL_OPTIONS = {
    httpOnly: true,
    path: "/",
    expires: new Date(0),
    secure: "development" !== process.env.NODE_ENV,
};

export const accessTokenFromCookies = (cookies: Partial<{ [p: string]: string }>): string | null => {
    return cookies[APP_COOKIES_ACCESS] || null;
};

export const refreshTokenFromCookies = (cookies: NextCookies): string | null => {
    const auth = cookies.get(APP_COOKIES_AUTH);

    if (auth) {
        const { refresh_token } = JSON.parse(auth);
        return refresh_token;
    }

    return null;
};
