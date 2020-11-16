from config import CALC_FORMANT_INTERVAL
import scipy.signal
import numpy as np

def get_formant(sound_list:list):
    sound_list = np.array([value/32768.0 for value in sound_list])
    num_sound_list = len(sound_list)

    result_x,result_y = [],[]
    
    for s in range(0,num_sound_list,CALC_FORMANT_INTERVAL):
        start,stop = s,s+CALC_FORMANT_INTERVAL
        s_list = sound_list[start:stop]
        N = len(s_list)
        i = 0
        while 2**i < N:
            i+= 1
        blank = 2**i - N
        bef = blank //2
        aft = blank - bef
        s_list = [0.]*bef + s_list.tolist() + [0.]*aft
        N = 2**i

        w = scipy.signal.hanning(N)
        s_list = s_list * w
        dft = np.fft.fft(s_list)


        Adft = np.abs(dft)
        Pdft = np.abs(dft)**2
        fscale = np.fft.fftfreq(len(dft),d=1.0/44100)
        Pdft_dB = 10*np.log10(Pdft[:N//2])

        cps = np.fft.ifft(Pdft_dB)
        quefrency = np.arange(0,44100,44100/N)

        cepCoef = 20
        cps_lif = np.array(cps)
        cps_lif[cepCoef:len(cps_lif)-cepCoef+1] =0
        dftSpc = np.fft.fft(cps_lif)

        _fscale =  np.array(fscale[:N//2])
        dftSpc = dftSpc[(_fscale < 5000.)]
        fscale = fscale[:len(dftSpc)]

        maximal_idx = scipy.signal.argrelmax(dftSpc,order=30)
        base = min(dftSpc)+(max(dftSpc)-min(dftSpc))/3
        
        maximal_idx = [ i for i in maximal_idx[0] if dftSpc[i] > base]
        if len(maximal_idx) >= 2:
            result_x += [fscale[maximal_idx[0]]]
            result_y += [fscale[maximal_idx[1]]]
    return result_x,result_y


if __name__ == "__main__":
    f = [2*np.sin(value*np.pi/180)+np.sin(2*value*np.pi/180) for value in range(44100)]
    x,y = get_formant(f)
    print(x)
    print(y)